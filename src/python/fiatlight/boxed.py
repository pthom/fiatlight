from typing import TypeVar, Generic, TypeAlias

T = TypeVar("T")


class BoxedImmutableData(Generic[T]):
    """A class that enables to transform python immutable types (int, float, str, bool, etc.)
    into mutable types.
    """

    value: T

    def __init__(self, value: T) -> None:
        self.value = value


BoxedInt: TypeAlias = BoxedImmutableData[int]
BoxedFloat: TypeAlias = BoxedImmutableData[float]
BoxedStr: TypeAlias = BoxedImmutableData[str]
BoxedBool: TypeAlias = BoxedImmutableData[bool]
