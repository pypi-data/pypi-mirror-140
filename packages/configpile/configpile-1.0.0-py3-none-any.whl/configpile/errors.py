from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    overload,
)

if TYPE_CHECKING:
    from .arg import Param


class Err(ABC):
    """
    Describes an error that occurred during argument parsing
    """

    @abstractmethod
    def markdown(self) -> Sequence[str]:
        pass

    @abstractmethod
    def errors(self) -> Sequence[Err]:
        pass


class SingleErr(Err):
    def errors(self) -> Sequence[Err]:
        return [self]


@dataclass
class GenErr(SingleErr):
    msg: str

    def markdown(self) -> Sequence[str]:
        return [self.msg]


@dataclass
class ArgErr(SingleErr):
    arg: Param[Any]
    err: Err

    def markdown(self) -> Sequence[str]:
        return [f"Error while processing argument {self.arg.name}:", "", *self.err.markdown()]


@dataclass
class ManyErr(Err):

    errs: Sequence[Err]

    def __post_init__(self) -> None:
        assert len(self.errs) > 0, "A ManyErr should contain at least one error"

    def markdown(self) -> Sequence[str]:
        lines: List[str] = []
        for i, e in enumerate(self.errs):
            start = f"{i+1}. "
            res: Sequence[str] = e.markdown()
            if res:
                line1 = start + res[0]

                def space_prefix(s: str) -> str:
                    return (" " * len(start)) + s

                rest: List[str] = [space_prefix(l) for l in res[1:]]
                lines.append(line1)
                lines.extend(rest)
        return lines

    def errors(self) -> Sequence[Err]:
        return self.errs


@dataclass(frozen=True)
class ParseErr(SingleErr):
    msg: str
    string: str  #: String value that could not be parsed
    index: Optional[int]  #: Position of the parse error, if known

    def markdown(self) -> Sequence[str]:
        parse_msg = f"Parse error in `{self.string}`"
        if self.index is not None:
            parse_msg += f" at index {self.index}"
        return [self.msg, "", parse_msg]


#: Ok value in our custom result type
T = TypeVar("T", covariant=True)

U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


Result = Union[T, Err]


def collect_seq(seq: Sequence[Result[T]]) -> Result[Sequence[T]]:
    ok: List[T] = []
    errs: List[Err] = []
    for res in seq:
        if isinstance(res, Err):
            errs.extend(res.errors())
        else:
            ok.append(res)
    if errs:
        return ManyErr(errs)
    else:
        return ok


@overload
def collect(t: Result[T], u: Result[U]) -> Result[Tuple[T, U]]:
    pass


@overload
def collect(t: Result[T], u: Result[U], v: Result[V]) -> Result[Tuple[T, U, V]]:
    pass


@overload
def collect(
    t: Result[T],
    u: Result[U],
    v: Result[V],
    w: Result[W],
) -> Result[Tuple[T, U, V, W]]:
    pass


def collect(*args):  # type: ignore[no-untyped-def]
    ok: List[Any] = []
    errs: List[Err] = []
    for arg in args:
        if isinstance(arg, Err):
            errs.extend(arg.errors())
        else:
            ok.append(arg)
    if errs:
        return ManyErr(errs)
    else:
        return tuple(ok)


def map_result(f: Callable[[T], U], r: Result[T]) -> Result[U]:
    if isinstance(r, Err):
        return r
    else:
        return f(r)
