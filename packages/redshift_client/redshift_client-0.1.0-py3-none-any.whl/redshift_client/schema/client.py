from dataclasses import (
    dataclass,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.frozen import (
    FrozenDict,
)
from fa_purity.json.primitive.factory import (
    to_primitive,
)
from fa_purity.utils import (
    raise_exception,
)
from redshift_client.schema.core import (
    SchemaId,
)
from redshift_client.sql_client.core import (
    InvalidType,
    SqlClient,
)
from redshift_client.sql_client.query import (
    dynamic_query,
    new_query,
)
from redshift_client.table.core import (
    TableId,
)
from typing import (
    FrozenSet,
    TypeVar,
)

_T = TypeVar("_T")


def _assert_bool(raw: _T) -> bool:
    if isinstance(raw, bool):
        return raw
    raise InvalidType("Expected bool")


@dataclass(frozen=True)
class SchemaClient:
    _db_client: SqlClient

    def all_schemas(self) -> Cmd[FrozenSet[SchemaId]]:
        stm = (
            "SELECT s.nspname AS table_schema"
            "FROM pg_catalog.pg_namespace s "
            "JOIN pg_catalog.pg_user u ON u.usesysid = s.nspowner "
            "ORDER BY table_schema"
        )
        return self._db_client.execute(
            new_query(stm), None
        ) + self._db_client.fetch_all().map(
            lambda i: frozenset(
                SchemaId(to_primitive(e[0], str).unwrap()) for e in i
            )
        )

    def table_ids(self, schema: SchemaId) -> Cmd[FrozenSet[TableId]]:
        stm: str = (
            "SELECT tables.table_name FROM information_schema.tables "
            "WHERE table_schema = %(schema_name)s"
        )
        return self._db_client.execute(
            new_query(stm), FrozenDict({"schema_name": schema._name})
        ) + self._db_client.fetch_all().map(
            lambda i: frozenset(
                TableId(schema, to_primitive(e[0], str).unwrap()) for e in i
            )
        )

    def exist(self, schema: SchemaId) -> Cmd[bool]:
        stm: str = (
            "SELECT EXISTS"
            "(SELECT 1 FROM pg_namespace "
            "WHERE nspname = %(schema_name)s)"
        )
        return self._db_client.execute(
            new_query(stm), FrozenDict({"schema_name": schema._name})
        ) + self._db_client.fetch_one().map(
            lambda i: _assert_bool(i[0])
            if i is not None
            else raise_exception(InvalidType("Expected not None"))
        )

    def delete(self, schema: SchemaId, cascade: bool) -> Cmd[None]:
        opt = " CASCADE" if cascade else ""
        stm: str = "DROP SCHEMA {schema_name}" + opt
        return self._db_client.execute(
            dynamic_query(stm, FrozenDict({"schema_name": schema._name})), None
        )

    def rename(self, old: SchemaId, new: SchemaId) -> Cmd[None]:
        stm = "ALTER SCHEMA {from_schema} RENAME TO {to_schema}"
        return self._db_client.execute(
            dynamic_query(
                stm,
                FrozenDict(
                    {
                        "from_schema": old._name,
                        "to_schema": new._name,
                    }
                ),
            ),
            None,
        )
