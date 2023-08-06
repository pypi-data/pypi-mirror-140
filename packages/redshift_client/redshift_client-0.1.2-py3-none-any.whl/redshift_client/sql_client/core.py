from dataclasses import (
    dataclass,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from logging import (
    Logger,
)
from psycopg2 import (
    extras,
)
from redshift_client.sql_client import (
    _assert,
)
from redshift_client.sql_client.connection import (
    DbConnection,
)
from redshift_client.sql_client.query import (
    Query,
)
from typing import (
    Any,
    Optional,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from psycopg2 import (
        cursor as CursorStub,
    )
else:
    CursorStub = Any
InvalidType = _assert.InvalidType
InvalidAssumption = _assert.InvalidAssumption
PrimitiveVal = _assert.PrimitiveVal


@dataclass(frozen=True)
class SqlClient:
    _log: Logger
    _cursor: CursorStub

    def execute(
        self, query: Query, values: Optional[FrozenDict[str, PrimitiveVal]]
    ) -> Cmd[None]:
        _values = values if values else FrozenDict({})
        preview: str = self._cursor.mogrify(query._inner.statement, _values)  # type: ignore[no-untyped-call]

        def _action() -> None:
            self._log.debug("Executing: %s", preview)
            self._cursor.execute(query._inner.statement, _values)  # type: ignore[no-untyped-call]

        return Cmd.from_cmd(_action)

    def batch(
        self, query: Query, args: FrozenList[FrozenDict[str, PrimitiveVal]]
    ) -> Cmd[None]:
        def _action() -> None:
            self._log.debug(
                "Batch execution (%s items): %s",
                len(args),
                query._inner.statement,
            )
            extras.execute_batch(self._cursor, query._inner.statement, args)

        return Cmd.from_cmd(_action)

    def fetch_one(self) -> Cmd[Optional[FrozenList[PrimitiveVal]]]:
        def _action() -> Optional[FrozenList[PrimitiveVal]]:
            return _assert.assert_fetch_one(self._cursor.fetchone())  # type: ignore[misc]

        return Cmd.from_cmd(_action)

    def fetch_all(self) -> Cmd[FrozenList[FrozenList[PrimitiveVal]]]:
        def _action() -> FrozenList[FrozenList[PrimitiveVal]]:
            return _assert.assert_fetch_all(tuple(self._cursor.fetchall()))  # type: ignore[misc]

        return Cmd.from_cmd(_action)


def new_client(connection: DbConnection, log: Logger) -> Cmd[SqlClient]:
    def _action() -> SqlClient:
        return SqlClient(log, connection._inner._connection.cursor())

    return Cmd.from_cmd(_action)
