# these are mostly just exports, #noqa them so flake8 will be happy
from dbt.adapters.cratedbadapter.connections import CratedbAdapterConnectionManager # noqa
from dbt.adapters.cratedbadapter.connections import CratedbAdapterCredentials
from dbt.adapters.cratedbadapter.relation import CratedbAdapterColumn  # noqa
from dbt.adapters.cratedbadapter.relation import CratedbAdapterRelation  # noqa: F401
from dbt.adapters.cratedbadapter.impl import CratedbAdapterAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import cratedbadapter

Plugin = AdapterPlugin(
    adapter=CratedbAdapterAdapter,
    credentials=CratedbAdapterCredentials,
    include_path=cratedbadapter.PACKAGE_PATH,
    dependencies=['postgres'])