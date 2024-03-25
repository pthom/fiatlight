from typing import Any, Callable, TypeAlias, TypeVar


DataType = TypeVar("DataType")


Function: TypeAlias = Callable[..., Any]

VoidFunction = Callable[[], None]
BoolFunction = Callable[[], bool]
