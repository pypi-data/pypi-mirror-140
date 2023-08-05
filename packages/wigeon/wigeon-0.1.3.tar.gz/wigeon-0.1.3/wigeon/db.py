# standard imports
import pathlib as pl
import os
import sqlite3
import datetime
from typing import Union, List

# external imports
# import pyodbc
import pymssql

# project imports
from wigeon.manifests import Environment, Manifest

class Connector(object):

    db_engines = [
        "sqlite",
        "mssql",
        "postgres"
    ]

    def __init__(
        self,
        manifest: Manifest,
        environment: Environment
    ):
        self.db_engine = manifest["db_engine"]
        self.manifest = manifest
        self.environment = environment
        self.cnxn = None
        self.changeloginit = {
            "sqlite": "CREATE TABLE IF NOT EXISTS changelog (change_id INTEGER NOT NULL PRIMARY KEY, migration_date TEXT, migration_name TEXT, applied_by TEXT);",
            "mssql":  """CREATE TABLE changelog (change_id INT NOT NULL IDENTITY PRIMARY KEY, migration_date TEXT, migration_name TEXT, applied_by TEXT);"""
        }[self.db_engine]


    def connect(
        self,
        **kwargs
    ):
        db_engines = {
            "sqlite": self.conn_sqlite,
            "mssql": self.conn_mssql,
            "postgres": self.conn_postgres
        }
       
       # read environment name from Connector and collect envvariable names
       # extract environment variables to kwargs if variables exist
        if self.environment:
            print(f"Connecting to {self.db_engine} via environment variables...", end=" ")
            kwargs = self.environment
            # dictionary comprehension ftwftwftw
            kwargs = {k:os.environ[v] for k,v in kwargs.items() if v}

         # run connection method based on db_engine for package
        db_engines[self.db_engine](**kwargs)
        return self.cnxn
        

    def conn_sqlite(
        self,
        **kwargs
    ) -> sqlite3.Connection:
        """
        Connect to a sqlite database and return connection
        """
        if kwargs["connectionstring"]:
            self.cnxn = sqlite3.connect(kwargs["connectionstring"])
            return self.cnxn
        else:
            raise ValueError("sqlite connection requires connectionstring argument only (the filepath)")
    
    def conn_postgres(self, **kwargs):
        raise NotImplementedError("conn_postgres is not yet implemented!")
    
    def conn_mssql(
        self,
        **kwargs
    ) -> pymssql.Connection:
        """
        Connect to a sql server database and return connection
        
        server requires host and port example: "0.0.0.0:1433"
        """
        try:
            kwargs["connectionstring"]
            raise NotImplementedError("connectionstring not yet supported for mssql connection")
        except:
            pass
        self.cnxn = pymssql.connect(
            server=kwargs["server"],
            user=kwargs["username"],
            password=kwargs["password"],
            database=kwargs["database"]
        )
        return self.cnxn

class Migration(object):

    def __init__(
        self,
        name: str,
        builds: List[str]
    ):
        self.name = name
        self.builds = builds
    
    def __str__(self):
        return f"name: {self.name}, builds: {self.builds}"
    
    def __repr__(self):
        return f"name: {self.name}, builds: {self.builds}"

    def run(
        self,
        package_path: pl.Path,
        cursor: Union[sqlite3.Cursor, pymssql.Cursor],
        user: str,
        db_engine: str
    ):
        with open(package_path.joinpath(self.name), "r") as f:
            query = f.read()
        
        try:
            cursor.execute(query)
        except Exception as e:
            if db_engine == "sqlite":
                cursor.execute("ROLLBACK")
                raise e
            if db_engine == "mssql":
                raise e
                

        migration_date = datetime.datetime.now().strftime("%Y%m%d-%H%M")

        if db_engine == "sqlite":
            cursor.execute(
                "INSERT INTO changelog (migration_date, migration_name, applied_by) VALUES(:migration_date, :migration_name, :applied_by)",
                {
                    "migration_date": migration_date,
                    "migration_name": self.name,
                    "applied_by": user
                }
            )
        if db_engine == "mssql":
            cursor.execute(
                "INSERT INTO changelog (migration_date, migration_name, applied_by) VALUES (%s, %s, %s)",
                (migration_date, self.name, user)
            )