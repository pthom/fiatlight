from typing import Callable, Any, TypeAlias

PureFunction: TypeAlias = Callable[..., Any]

VoidFunction = Callable[[], None]
BoolFunction = Callable[[], bool]
