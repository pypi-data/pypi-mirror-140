from dbt.adapters.base import Column
from dataclasses import dataclass
from dbt.adapters.base.relation import BaseRelation
from dbt.exceptions import RuntimeException

from dbt.adapters.base import Column
from dataclasses import dataclass
from dbt.adapters.postgres.relation import PostgresRelation
from dbt.contracts.graph.parsed import ParsedSourceDefinition, ParsedNode
from dbt.utils import filter_null_values, deep_merge, classproperty

from typing import (
    Optional, TypeVar, Any, Type, Dict, Union, Iterator, Tuple, Set
)
from dbt.contracts.relation import (
    RelationType, ComponentName, HasQuoting, FakeAPIObject, Policy, Path
)

Self = TypeVar('Self', bound='BaseRelation')

@dataclass(frozen=True, eq=False, repr=False)
class CratedbAdapterRelation(BaseRelation):
    def relation_max_name_length(self):
        return 63

class CratedbAdapterColumn(Column):
    pass  # redshift does not inherit from postgres here
