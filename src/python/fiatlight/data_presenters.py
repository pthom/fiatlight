from imgui_bundle import imgui, hello_imgui
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import SourceWithGui

from typing import Any
from dataclasses import dataclass
from enum import Enum


class IntEditType(Enum):
    slider = 1
    input = 2


@dataclass
class IntEditParams:
    label: str = "##int"
    v_min: int = 0
    v_max: int = 10
    width_em: float = 10
    edit_type: IntEditType = IntEditType.slider


def _present_str(x: Any) -> None:
    imgui.text(str(x))


def make_int_with_gui(initial_value: int, params: IntEditParams | None = None) -> AnyDataWithGui:
    if params is None:
        params = IntEditParams()
    r = AnyDataWithGui()
    r.value = initial_value
    r.gui_present_impl = lambda: _present_str(r.value)
    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        if params.edit_type == IntEditType.slider:
            imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
            changed, r.value = imgui.slider_int(params.label, r.value, params.v_min, params.v_max)
        elif params.edit_type == IntEditType.input:
            imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
            changed, r.value = imgui.input_int(params.label, r.value)

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


def make_int_source(initial_value: int, params: IntEditParams | None = None, label: str = "Source") -> SourceWithGui:
    x = make_int_with_gui(initial_value, params)
    return SourceWithGui(x, label)


# def make_int_editor(x: BoxedInt, params: IntEditParams | None = None) -> EditParameterGui:
#     if params is None:
#         params = IntEditParams()
#
#     def edit() -> bool:
#         return edit_int(params, x)
#
#     return edit


# def make_int_with_gui(x: int, params: IntEditParams) -> AnyDataWithGui:
#
#     class _IntWithGui(AnyDataWithGui):
#         def __init__(self):
#             self.value = x
#         def gui_data(self, label: str) -> None:
#             imgui.text(f"{label}: {self.value}")


# def make_int_source(label: str, initial_value: int, params: IntEditParams) -> SourceWithGui:
#     x = BoxedInt(initial_value)
#
#     def edit() -> bool:
#         return edit_int(params, x)
#
#     def present() -> None:
#         imgui.text(f"{label}: {x.value}")
#
#     return SourceWithGui(edit, present)


__all__ = [
    # Ints
    "IntEditParams",
    "IntEditType",
    "make_int_with_gui",
]
