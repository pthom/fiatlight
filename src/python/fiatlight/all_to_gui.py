from fiatlight.to_gui import TypeToGuiHandlers
from fiatlight.standard_gui_handlers import (
    make_int_gui_handlers,
    make_str_gui_handlers,
    make_bool_gui_handlers,
    make_float_gui_handlers,
    IntWithGuiParams,
    StrWithGuiParams,
    BoolWithGuiParams,
    FloatWithGuiParams,
)

from typing import List


_ALL_TYPE_TO_GUI_INFO: List[TypeToGuiHandlers] = [
    TypeToGuiHandlers(int, make_int_gui_handlers, IntWithGuiParams()),
    TypeToGuiHandlers(float, make_float_gui_handlers, FloatWithGuiParams()),
    TypeToGuiHandlers(str, make_str_gui_handlers, StrWithGuiParams()),
    TypeToGuiHandlers(bool, make_bool_gui_handlers, BoolWithGuiParams()),
    TypeToGuiHandlers(List[str], make_bool_gui_handlers, BoolWithGuiParams()),
    TypeToGuiHandlers(List[bool], make_bool_gui_handlers, BoolWithGuiParams()),
]


def all_type_to_gui_info() -> List[TypeToGuiHandlers]:
    return _ALL_TYPE_TO_GUI_INFO


__all__ = ["all_type_to_gui_info", "TypeToGuiHandlers"]
