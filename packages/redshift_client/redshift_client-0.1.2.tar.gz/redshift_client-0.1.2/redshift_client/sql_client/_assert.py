from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from fa_purity.json.primitive.core import (
    is_primitive,
    Primitive,
)
from fa_purity.result import (
    Result,
    ResultE,
    UnwrapError,
)
from fa_purity.utils import (
    raise_exception,
)
from typing import (
    Callable,
    Optional,
    TypeVar,
    Union,
)


class InvalidType(Exception):
    pass


class InvalidAssumption(Exception):
    pass


PrimitiveVal = Union[Primitive, datetime]

_A = TypeVar("_A")
_T = TypeVar("_T")
_R = TypeVar("_R")


def _assert_prim_val(raw: _T) -> ResultE[PrimitiveVal]:
    if is_primitive(raw) or isinstance(raw, datetime):
        return Result.success(raw)
    return Result.failure(
        InvalidType(f"Got {type(raw)}; expected a PrimitiveVal")
    )


def _assert_list_of(
    items: _A, assertion: Callable[[_T], ResultE[_R]]
) -> ResultE[FrozenList[_R]]:
    try:
        if isinstance(items, tuple):
            return Result.success(tuple(assertion(i).unwrap() for i in items))
        return Result.failure(InvalidType("Expected tuple"))
    except UnwrapError[FrozenList[_R], Exception] as err:
        return Result.failure(err.container.unwrap_fail())


def assert_fetch_one(
    result: Optional[_T],
) -> Optional[FrozenList[PrimitiveVal]]:
    if result is None:
        return result
    err = InvalidAssumption(f"Unexpected fetch_one result; got {type(result)}")
    if isinstance(result, tuple):
        return (
            _assert_list_of(result, _assert_prim_val)
            .alt(lambda _: err)
            .alt(raise_exception)
            .unwrap()
        )
    raise err


def assert_fetch_all(result: _T) -> FrozenList[FrozenList[PrimitiveVal]]:
    err = InvalidAssumption(f"Unexpected fetch_all result; got {type(result)}")
    _assert: Callable[
        [_R], ResultE[FrozenList[PrimitiveVal]]
    ] = lambda l: _assert_list_of(l, _assert_prim_val)
    if isinstance(result, tuple):
        return (
            _assert_list_of(result, _assert)
            .alt(lambda _: err)
            .alt(raise_exception)
            .unwrap()
        )
    raise err
