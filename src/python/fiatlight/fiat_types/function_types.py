from typing import Any, Callable, TypeAlias


Function: TypeAlias = Callable[..., Any]
VoidFunction = Callable[[], None]
BoolFunction = Callable[[], bool]
