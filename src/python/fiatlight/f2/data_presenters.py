from imgui_bundle import imgui
from fiatlight.f2.boxed import BoxedInt, BoxedFloat, BoxedStr, BoxedBool
from fiatlight.f2.parameter_with_gui import EditParameterGui, PresentParameterGui

from dataclasses import dataclass
from enum import Enum


class IntEditType(Enum):
    SLIDER = 1
    INPUT = 2


@dataclass
class IntEditParams:
    label: str = "##int"
    v_min: int = 0
    v_max: int = 10
    edit_type: IntEditType = IntEditType.SLIDER


def edit_int(params: IntEditParams, x: BoxedInt) -> bool:
    changed = False
    if params.edit_type == IntEditType.SLIDER:
        changed, x.value = imgui.slider_int(params.label, x.value, params.v_min, params.v_max)
    elif params.edit_type == IntEditType.INPUT:
        changed, x.value = imgui.input_int(params.label, x.value)
    return changed


def make_int_editor(
    x: BoxedInt,
    label: str = "##int",
    v_min: int = 0,
    v_max: int = 10,
    edit_type: IntEditType = IntEditType.SLIDER,
) -> EditParameterGui:
    params = IntEditParams(label, v_min, v_max, edit_type)

    def edit() -> bool:
        return edit_int(params, x)

    return edit


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
