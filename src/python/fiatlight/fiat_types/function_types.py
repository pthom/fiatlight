from typing import Any, Callable, TypeAlias, Tuple, List
from fiatlight.fiat_types.base_types import DataType


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


class DataValidationResult:
    """DataValidationResult: a result of a data validation function"""

    is_valid: bool
    error_message: str

    def __init__(self, secret: int) -> None:
        if secret != 42:
            raise ValueError(
                "This class should not be instantiated directly. Use DataValidationResult.ok() or DataValidationResult.error()"
            )

    @staticmethod
    def ok() -> "DataValidationResult":
        r = DataValidationResult(42)
        r.is_valid = True
        r.error_message = ""
        return r

    @staticmethod
    def error(error_message: str) -> "DataValidationResult":
        r = DataValidationResult(42)
        r.is_valid = False
        r.error_message = error_message
        return r

    def __str__(self) -> str:
        if self.is_valid:
            return "DataValidationResult.ok()"
        else:
            return f"DataValidationResult.error('{self.error_message}')"

    def __bool__(self) -> bool:
        return self.is_valid


# A function that validates a DataType value. Can be used when the user tries to set a value.
DataValidationFunction = Callable[[DataType], DataValidationResult]
