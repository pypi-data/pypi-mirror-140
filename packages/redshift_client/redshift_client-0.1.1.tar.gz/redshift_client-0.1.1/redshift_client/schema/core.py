from dataclasses import (
    dataclass,
)
from fa_purity.frozen import (
    FrozenDict,
)
from redshift_client.table.core import (
    Table,
    TableId,
)


@dataclass(frozen=True)
class SchemaId:
    _name: str


@dataclass(frozen=True)
class Schema:
    tables: FrozenDict[TableId, Table]
