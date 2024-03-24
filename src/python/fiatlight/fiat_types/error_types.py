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