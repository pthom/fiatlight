from typing import Any, Callable, TypeAlias, Tuple, List
from fiatlight.fiat_types.base_types import DataType


# A function that takes any arguments and returns any value.
Function: TypeAlias = Callable[..., Any]
# A list of functions.
FunctionList: TypeAlias = List[Function]

# A function that takes no arguments and returns nothing.
VoidFunction = Callable[[], None]
# A function that takes no arguments and returns a boolean. Used mainly for "edit" callbacks,
# inside AnyDataWithGuiCallbacks.
BoolFunction = Callable[[], bool]

# A Gui function that takes no arguments and returns nothing. It should display ImGui widgets.
# Used mainly for "present" callbacks.
GuiFunction = Callable[[], None]
# A Gui function that takes no arguments and returns a boolean. Used mainly for "edit" callbacks.
GuiBoolFunction = Callable[[], bool]

# a Gui function that takes inputs and returns nothing. It should display ImGui widgets.
# Used mainly for GuiNode
GuiFunctionWithInputs = Callable[..., None]

# A function that takes a DataType value and returns a tuple of a tuple [modified, new_value]
# Used mainly for "edit" callbacks.
DataEditFunction = Callable[[DataType], Tuple[bool, DataType]]

# A function that takes a DataType value and returns nothing. Used mainly for "present" callbacks.
DataPresentFunction = Callable[[DataType], None]

# A function that validates a DataType value. Can be used when the user tries to set a value.
# It should raise a ValueError exception with a nice error message if the value is invalid.
# The error message will be shown to the user.
DataValidationFunction = Callable[[DataType], None]
