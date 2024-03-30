from typing import Any, Callable, TypeAlias, TypeVar, Tuple, List


# A type variable that represents a data type, included in a AnyDataWithGui object.
DataType = TypeVar("DataType")

# A type variable that represents a type that derives or implement AnyDataWithGui.
GuiType = TypeVar("GuiType")


Function: TypeAlias = Callable[..., Any]
FunctionList: TypeAlias = List[Function]

# A function that takes no arguments and returns nothing. Used mainly for "present" callbacks.
VoidFunction = Callable[[], None]

# A function that takes no arguments and returns a boolean. Used mainly for "edit" callbacks,
# inside AnyDataWithGuiCallbacks.
BoolFunction = Callable[[], bool]

# A function that takes a DataType value and returns a tuple of a tuple [modified, new_value]
# Used
DataEditFunction = Callable[[DataType], Tuple[bool, DataType]]

# A function that takes a DataType value and returns nothing. Used mainly for "present" callbacks.
DataPresentFunction = Callable[[DataType], None]
