from fiatlight.to_gui import TypeToGuiInfo
from fiatlight.data_presenters import (
    make_int_with_gui,
    make_str_with_gui,
    make_bool_with_gui,
    make_float_with_gui,
    IntWithGuiParams,
    StrWithGuiParams,
    BoolWithGuiParams,
    FloatWithGuiParams,
)

from typing import List


_ALL_TYPE_TO_GUI_INFO: List[TypeToGuiInfo] = [
    TypeToGuiInfo(int, make_int_with_gui, IntWithGuiParams()),
    TypeToGuiInfo(float, make_float_with_gui, FloatWithGuiParams()),
    TypeToGuiInfo(str, make_str_with_gui, StrWithGuiParams()),
    TypeToGuiInfo(bool, make_bool_with_gui, BoolWithGuiParams()),
]


def all_type_to_gui_info() -> List[TypeToGuiInfo]:
    return _ALL_TYPE_TO_GUI_INFO


__all__ = ["all_type_to_gui_info", "TypeToGuiInfo"]
