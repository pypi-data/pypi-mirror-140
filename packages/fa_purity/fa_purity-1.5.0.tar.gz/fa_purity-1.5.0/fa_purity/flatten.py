from fa_purity.cmd import (
    Cmd,
)
from fa_purity.cmd.transform import (
    serial_merge,
)
from fa_purity.frozen import (
    FrozenList,
)
from fa_purity.result import (
    Result,
    UnwrapError,
)
from typing import (
    TypeVar,
)

_T = TypeVar("_T")
_S = TypeVar("_S")
_F = TypeVar("_F")


def flatten_cmds(items: FrozenList[Cmd[_T]]) -> Cmd[FrozenList[_T]]:
    """serial_merge function alias"""
    return serial_merge(items)


def flatten_results(
    items: FrozenList[Result[_S, _F]]
) -> Result[FrozenList[_S], _F]:
    try:
        return Result.success(tuple(i.unwrap() for i in items))
    except UnwrapError[_S, _F] as err:
        return Result.failure(err.container.unwrap_fail())
