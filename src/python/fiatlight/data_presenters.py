from imgui_bundle import imgui
from fiatlight.any_data_with_gui import AnyDataWithGui

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
    edit_type: IntEditType = IntEditType.slider


def _present_str(x: Any) -> None:
    imgui.text(str(x))


def make_int_with_gui(initial_value: int, params: IntEditParams) -> AnyDataWithGui:
    r = AnyDataWithGui()
    r.value = initial_value
    r.gui_present_impl = lambda: _present_str(r.value)

    def edit() -> bool:
        changed = False
        if params.edit_type == IntEditType.slider:
            changed, r.value = imgui.slider_int(params.label, r.value, params.v_min, params.v_max)
        elif params.edit_type == IntEditType.input:
            changed, r.value = imgui.input_int(params.label, r.value)
        return changed

    r.gui_edit_impl = edit

    return r


# def make_int_source(label: str, initial_value: int, params: IntEditParams) -> SourceWithGui:
#     x = make_int_with_gui(initial_value, params)
#
#     def present() -> None:
#         imgui.text(f"{label}: {x.value}")
#
#     return SourceWithGui(x, present)


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
