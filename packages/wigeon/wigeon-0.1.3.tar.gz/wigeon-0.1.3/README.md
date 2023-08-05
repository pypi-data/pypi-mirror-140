# wigeon
[![Build and test](https://github.com/JLRitch/wigeon/actions/workflows/build-test.yml/badge.svg)](https://github.com/JLRitch/wigeon/actions/workflows/build-test.yml)

DB Migrations for the continuous developer.

## Why wigeon?
Your applications are continuously delivered, why not your databases too?

Like its namesake, wigeon is compact, portable, and easily able to fit itself into your
repos/actions/pipelines/etc. to complement the continuous patterns you worked so hard
to put into place.

Does not use an ORM or require language specific migration syntax meaning anyone
who can `SELECT *` can automate and continuously integrate/deliver data goodness
to their apps/teams.

## Features included
- Database package creation
- Migration manifest management
- Migration build tagging
- Connection manager
- Simple connection definitions via environment variables
- Migration changelog written to target database
- Deploy/run sql script migrations

## Databases supported (at the moment)
- sqlite
- mssqlserver
## Databases to support (soon)
- postgres
- mysql

## Setup
### Direct Install
```shell
pip install wigeon
```

### Via Docker-Compose
```shell
docker-compose up
```
Attach a shell to the wigeon_cli container. You can create packages/migrations and run them against
db services in the docker-compose network. Package files will write to your local compute using
volume mounts.

You can edit environment variable names in your local manifest.json which will propigate to the cli service,
where the values for those variables are read. To change your target database, you will need to edit env
variables in the docker-compose file.

## To use:
NOTE: prefix every command with `python` if you are running directly from a clone of the repo.

Access help:
```bash
wigeon --help
```

Create package with name `fly` for `sqlite` dbtype with local, dev, qa, and prod environments:
```bash
wigeon create package --name flytwo --dbtype sqlite --environments local,dev,qa,prod
```



Create databases to connect to for each environment:
```bash
sqlite3
.open fly-local.sqlite
.open fly-dev.sqlite
.open fly-qa.sqlite
.open fly-prod.sqlite
```

(OPTIONAL) Set up environment variables and add to package manifest.json:
```bash
export LOCAL_CONNECTION_STRING=/home/usr/wigeon/fly-local.sqlite
export DEV_CONNECTION_STRING=/home/usr/wigeon/fly-dev.sqlite
export QA_CONNECTION_STRING=/home/usr/wigeon/fly-qa.sqlite
export PROD_CONNECTION_STRING=/home/usr/wigeon/fly-prod.sqlite
```

(OPTIONAL) Config add env variable names for connectionstring of each environment in the `fly` package:
```bash
wigeon config --name fly --environment local --conn_string LOCAL_CONNECTION_STRING
wigeon config --name fly --environment dev --conn_string DEV_CONNECTION_STRING
wigeon config --name fly --environment qa --conn_string QA_CONNECTION_STRING
wigeon config --name fly --environment prod --conn_string PROD_CONNECTION_STRING
```

(OPTIONAL) If running mssql in docker you might Set up environment variables and
add to package manifest.json:
```bash
export LOCAL_MSSQL_SERVER=0.0.0.0:1433 # or 127.0.0.1
export LOCAL_MSSQL_DBNAME=tempdb
export LOCAL_MSSQL_USERNAME=sa
export LOCAL_MSSQL_PASSWORD=SApass123
```

(OPTIONAL) Config add env variable names for connectionstring of each environment in the `fly` package:
```bash
wigeon config --name fly --environment local --server LOCAL_MSSQL_SERVER --database LOCAL_MSSQL_DBNAME --username LOCAL_MSSQL_USERNAME --password LOCAL_MSSQL_PASSWORD
```

(OPTIONAL) Add environment variable names directly to manifest.json:
```json
  "environments": {
      "local": {
          "connectionstring": "LOCAL_CONNECTION_STRING",
          "server": null,
          "database": null,
          "username": null,
          "password:": null
      },
      "dev": {
          "connectionstring": "DEV_CONNECTION_STRING",
          "server": null,
          "database": null,
          "username": null,
          "password:": null
      },
      "qa": {
          "connectionstring": "QA_CONNECTION_STRING",
          "server": null,
          "database": null,
          "username": null,
          "password:": null
      },
      "prod": {
          "connectionstring": "PROD_CONNECTION_STRING",
          "server": null,
          "database": null,
          "username": null,
          "password:": null
      }
  }
```

Add migrations to the `fly` package with build tag of `0.0.1`:
```bash
wigeon create migration --name initialize_db --package fly --build 0.0.1
wigeon create migration --name add_habitat_table --package fly --build 0.0.1
wigeon create migration --name add_paths_table --package fly --build 0.0.1
```

**SCRIPT SOME SQL IN THOSE MIGRATION FILES!!!**

List all migrations for the `fly` package:
```bash
wigeon show --name fly --migrations
```

Run connection test to the `fly` package's local environment:
```bash
wigeon migrate --name fly --connect_test --environment local
```

Run migrations for the `fly` package (a local sqlite connection):
```bash
wigeon migrate --name fly --conn_string=/path/to/exampledb.sqlite
```

OR

IF package's manifest.json is configured appropriately for a "local" environment
```bash
wigeon migrate --name fly --environment local
```

## Requirements (ODBC future support)

### For gcc compiler on Ubuntu
```bash
sudo apt install build-essential
```
### For ODBC on Ubuntu
```bash
sudo apt-get install libssl-dev libffi-dev python3-dev
sudo apt-get install -y unixodbc-dev
```

### For mssql-server ODBC on Ubuntu
Docs for installing sqlserver odbc drivers (not yet supported):
https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15

## running tests
```bash
 python -m pytest --cov-report term-missing --cov=wigeon test/
 ```