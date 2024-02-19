from typing import Generic, TypeVar, Callable, TypeAlias


T = TypeVar("T")


# Any function that can present an editable GUI for a given parameter
EditParameterGui: TypeAlias = Callable[[], bool]
# Any function that can present a short visual GUI for a given parameter
PresentParameterGui: TypeAlias = Callable[[], None]


class ParameterWithGui(Generic[T]):
    """A class that represents a parameter of a function,
    with an optional GUI to edit it, and an optional GUI to present it"""

    name: str
    value: T | None
    edit_gui: EditParameterGui | None
    present_gui: PresentParameterGui | None

    def __init__(
        self,
        name: str,
        value: T | None = None,
        edit_gui: EditParameterGui | None = None,
        present_gui: PresentParameterGui | None = None,
    ) -> None:
        self.name = name
        self.value = value
        self.edit_gui = edit_gui
        self.present_gui = present_gui
