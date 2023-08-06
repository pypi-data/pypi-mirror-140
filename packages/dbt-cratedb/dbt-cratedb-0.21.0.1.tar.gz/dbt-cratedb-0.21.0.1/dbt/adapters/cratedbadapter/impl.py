from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Set, List, Any
from dbt.adapters.base.meta import available
from dbt.adapters.base.impl import AdapterConfig
from dbt.adapters.sql import SQLAdapter
from dbt.adapters.postgres import PostgresAdapter
from dbt.adapters.cratedbadapter import CratedbAdapterConnectionManager
from .relation import CratedbAdapterRelation
from .relation import CratedbAdapterColumn
from dbt.logger import GLOBAL_LOGGER as logger  # noqa
from dbt.dataclass_schema import dbtClassMixin, ValidationError
import dbt.exceptions
import dbt.utils

@dataclass
class CratedbConfig(AdapterConfig):
    unlogged: Optional[bool] = None

class CratedbAdapterAdapter(SQLAdapter):
    Relation = CratedbAdapterRelation
    ConnectionManager = CratedbAdapterConnectionManager
    Column = CratedbAdapterColumn

    AdapterSpecificConfigs = CratedbConfig

    @classmethod
    def date_function(cls):
        return 'now()'

    @available
    def verify_database(self, database):
        if database.startswith('"'):
            database = database.strip('"')
        expected = self.config.credentials.database
        if database.lower() != expected.lower():
            raise dbt.exceptions.NotImplementedException(
                'Cross-db references not allowed in {} ({} vs {})'
                    .format(self.type(), database, expected)
            )
        # return an empty string on success so macros can call this
        return ''


    def _get_catalog_schemas(self, manifest):
        # postgres only allow one database (the main one)
        schemas = super()._get_catalog_schemas(manifest)
        try:
            return schemas.flatten()
        except dbt.exceptions.RuntimeException as exc:
            dbt.exceptions.raise_compiler_error(
                'Cross-db references not allowed in adapter {}: Got {}'.format(
                        self.type(), exc.msg
                )
            )


