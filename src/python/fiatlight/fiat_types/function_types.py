from typing import Any, Callable, TypeAlias, Tuple, List
from fiatlight.fiat_types.base_types import DataType


Function: TypeAlias = Callable[..., Any]
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

# a Task function that takes inputs and returns nothing. It should perform a task (e.g. save a file).
# Used mainly for TaskNode
TaskFunctionWithInputs = Callable[..., None]


# A function that takes a DataType value and returns a tuple of a tuple [modified, new_value]
# Used
DataEditFunction = Callable[[DataType], Tuple[bool, DataType]]

# A function that takes a DataType value and returns nothing. Used mainly for "present" callbacks.
DataPresentFunction = Callable[[DataType], None]

# A function that validates a DataType value. Can be used when the user tries to set a value.
# It should raise a ValueError exception with a nice error message if the value is invalid.
# The error message will be shown to the user.
DataValidationFunction = Callable[[DataType], None]
