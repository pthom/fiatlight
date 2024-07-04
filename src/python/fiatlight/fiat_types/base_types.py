from typing import Any, TypeVar, Generic, List, NewType
from dataclasses import dataclass

# A type variable that represents a data type, included in a AnyDataWithGui object.
DataType = TypeVar("DataType")

# A type variable that represents a type that derives or implement AnyDataWithGui.
GuiType = TypeVar("GuiType")


#
# For DataType who can take a fixed set of values
#
@dataclass
class ExplainedValue(Generic[DataType]):
    """An explained possible value for a given type"""

    value: DataType
    label: str
    tooltip: str


# A list of explained possible values for a given type
ExplainedValues = List[ExplainedValue[DataType]]


# Types for serialization/deserialization
JsonPrimitive = str | int | float | bool | None
JsonDict = dict[str, Any]
JsonPrimitiveOrDict = JsonPrimitive | JsonDict

# Type for fiat attributes
FiatAttributes = NewType("FiatAttributes", dict[str, Any])
