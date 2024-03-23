from typing import Any, TypeAlias, TypeVar

DataType = TypeVar("DataType")

JsonPrimitive = str | int | float | bool | None
JsonDict = dict[str, Any]
JsonPrimitiveOrDict = JsonPrimitive | JsonDict

GlobalsDict: TypeAlias = dict[str, Any]
LocalsDict: TypeAlias = dict[str, Any]
