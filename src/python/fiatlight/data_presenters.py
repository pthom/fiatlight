from imgui_bundle import imgui
from fiatlight.boxed import BoxedInt, BoxedFloat, BoxedStr, BoxedBool
from fiatlight.parameter_with_gui import EditParameterGui, PresentParameterGui
# from fiatlight.function_with_gui import SourceWithGui

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


def edit_int(params: IntEditParams, x: BoxedInt) -> bool:
    changed = False
    if params.edit_type == IntEditType.slider:
        changed, x.value = imgui.slider_int(params.label, x.value, params.v_min, params.v_max)
    elif params.edit_type == IntEditType.input:
        changed, x.value = imgui.input_int(params.label, x.value)
    return changed


def make_int_editor(x: BoxedInt, params: IntEditParams | None = None) -> EditParameterGui:
    if params is None:
        params = IntEditParams()

    def edit() -> bool:
        return edit_int(params, x)

    return edit


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


def present_int(x: int) -> None:
    imgui.text(str(x))


def make_int_presenter(x: BoxedInt) -> PresentParameterGui:
    def present() -> None:
        present_int(x.value)

    return present


__all__ = [
    # Boxed types are reexported for convenience
    "BoxedInt",
    "BoxedFloat",
    "BoxedStr",
    "BoxedBool",
    # Ints
    "IntEditParams",
    "edit_int",
    "present_int",
    "make_int_editor",
    "make_int_presenter",
]
