from typing import Callable, Any, TypeAlias

PureFunction: TypeAlias = Callable[..., Any]

VoidFunction = Callable[[], None]
BoolFunction = Callable[[], bool]

JsonPrimitive = str | int | float | bool | None
JsonDict = dict[str, Any]
JsonPrimitiveOrDict = JsonPrimitive | JsonDict
