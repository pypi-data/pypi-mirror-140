from dataclasses import (
    dataclass,
)
from fa_purity.frozen import (
    FrozenDict,
)
from psycopg2.sql import (
    Identifier,
    SQL,
)
from typing import (
    cast,
    Optional,
)


def _purifier(
    statement: str, identifiers: FrozenDict[str, Optional[str]]
) -> SQL:
    raw_sql = SQL(statement)
    safe_args = FrozenDict(
        {key: Identifier(value) for key, value in identifiers.items()}
    )
    return cast(SQL, raw_sql.format(**safe_args))  # type: ignore[no-untyped-call]


@dataclass(frozen=True)
class _Query:
    statement: SQL


@dataclass(frozen=True)
class Query:
    _inner: _Query


def new_query(statement: str) -> Query:
    draft = _Query(SQL(statement))
    return Query(draft)


def dynamic_query(
    statement: str, identifiers: FrozenDict[str, Optional[str]]
) -> Query:
    draft = _Query(_purifier(statement, identifiers))
    return Query(draft)
