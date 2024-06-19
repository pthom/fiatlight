from dataclasses import dataclass

from fiatlight.fiat_types.base_types import DataType
from typing import Generic


class Unspecified:
    """A marker for an unspecified value, used as a default value for AnyDataWithGui.
    It is akin to None, but it is used to signal that the value has not been set yet.
    """

    def __init__(self, secret: int) -> None:
        if secret != 42:
            raise ValueError("UnspecifiedClass should not be instantiated directly, use the UnspecifiedValue constant")

    def __str__(self) -> str:
        return "Unspecified"


UnspecifiedValue = Unspecified(42)


class Error:
    """A marker for an error value, used as a default value for AnyDataWithGui.
    It is akin to None, but it is used to differentiate between a None value
    and a value that has been set to an error value, after a failed function call"""

    def __init__(self, secret: int) -> None:
        if secret != 42:
            raise ValueError("ErrorClass should not be instantiated directly, use the ErrorValue constant")

    def __str__(self) -> str:
        return "Error"


ErrorValue = Error(42)


@dataclass
class Invalid(Generic[DataType]):
    """A marker for an invalid value, used as a default value for AnyDataWithGui.
    It is akin to None, but it is used to differentiate between a None value
    and a value that has been set to an invalid value by the user,
    after a failed validation by a DataValidationFunction.
    """

    error_message: str
    invalid_value: DataType

    def info_error(self) -> str:
        return self.error_message

    def __str__(self) -> str:
        return f"{self.invalid_value} (Invalid)"
