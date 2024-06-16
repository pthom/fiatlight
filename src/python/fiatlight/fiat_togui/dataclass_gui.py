"""DataclassGui: adds a GUI to a dataclass

Usage example
=============

**Register the dataclass**

_Either with the decorator `@fl.dataclass_with_gui_registration`:_

    import fiatlight as fl

    @fl.dataclass_with_gui_registration(x__range=(0, 10))
    class MyParam:
        image_in: ImagePath
        x: int | None = None

_Or with `register_dataclass`:_

    from dataclasses import dataclass

    @dataclass
    class MyParam:
        image_in: ImagePath
        x: int | None = None

    from fiatlight.fiat_togui import register_dataclass
    register_dataclass(MyParam, x__range=(0, 10))

**Use the dataclass in a function:**

    def f(param: MyParam) -> MyParam:
        return param

    fiatlight.run(f)
"""

from fiatlight.fiat_core.togui_exception import FiatToGuiException
from typing import Type, Any
from .dataclass_like_gui import DataclassLikeGui, DataclassLikeType
from dataclasses import is_dataclass


class DataclassGui(DataclassLikeGui[DataclassLikeType]):
    """A sophisticated GUI for a dataclass type.
    Can edit and present all members of the dataclass.
    Can handle nested dataclasses.
    Can *not* serialize values
    """

    def __init__(self, dataclass_type: Type[DataclassLikeType], fiat_attributes: dict[str, Any] | None = None) -> None:
        if not is_dataclass(dataclass_type):
            raise FiatToGuiException(f"{dataclass_type} is not a dataclass")

        super().__init__(dataclass_type, fiat_attributes)  # type: ignore
