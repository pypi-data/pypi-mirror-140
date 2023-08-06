# dbt-cratedb
[dbt](https://www.getdbt.com) adapter for CrateDB.

Supports dbt 0.20

Easiest install is to use pip:

    pip install dbt-cratedb

## Authentication

'''
type: cratedbadapter
threads: 1
host: 20.94.130.194
port: 5432
user: crate
password: ""
database: ""
schema: dbt_dev
'''