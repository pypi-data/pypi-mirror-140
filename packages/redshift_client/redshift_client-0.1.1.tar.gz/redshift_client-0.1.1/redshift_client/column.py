from dataclasses import (
    dataclass,
)
from redshift_client.data_type.core import (
    DataType,
)


@dataclass(frozen=True)
class ColumnId:
    _name: str


@dataclass(frozen=True)
class Column:
    data_type: DataType
    nullable: bool
