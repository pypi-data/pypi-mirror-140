# standard imports
from typing import TypedDict, List

# external imports

# project imports

class Environment(TypedDict):
    connection_string: str
    server: str
    database: str
    username: str
    password: str

class Environments(TypedDict):
    environment: Environment

class Manifest(TypedDict):
    db_engine: str
    environments: dict
    migrations: List[str]
