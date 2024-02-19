from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import SourceWithGui


from typing import Any, Callable, TypeAlias
from dataclasses import dataclass
from enum import Enum


ImGuiKnobVariant_: TypeAlias = imgui_knobs.ImGuiKnobVariant_
ToggleConfig: TypeAlias = imgui_toggle.ToggleConfig


def _present_str(x: Any) -> None:
    imgui.text(str(x))


########################################################################################################################
#                               Ints
########################################################################################################################
class IntEditType(Enum):
    slider = 1
    input = 2
    drag = 3
    knob = 4


@dataclass
class IntEditParams:
    edit_type: IntEditType = IntEditType.slider
    # Common
    label: str = "##int"
    v_min: int = 0
    v_max: int = 10
    width_em: float = 10
    format: str = "%d"
    # Specific to slider_int and drag_int
    slider_flags: int = imgui.SliderFlags_.none.value
    # Specific to input_int
    input_flags: int = imgui.InputTextFlags_.none.value
    input_step: int = 1
    input_step_fast: int = 100
    # Specific to drag
    v_speed: float = 1.0
    # Specific to knob
    knob_speed: float = 0.0
    knob_variant: int = ImGuiKnobVariant_.tick.value
    knob_size_em: float = 2.5
    knob_steps: int = 0


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
        imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
        if params.edit_type == IntEditType.slider:
            changed, r.value = imgui.slider_int(
                params.label, r.value, params.v_min, params.v_max, params.format, params.slider_flags
            )
        elif params.edit_type == IntEditType.input:
            changed, r.value = imgui.input_int(
                params.label, r.value, params.input_step, params.input_step_fast, params.input_flags
            )
        elif params.edit_type == IntEditType.drag:
            changed, r.value = imgui.drag_int(
                params.label, r.value, params.v_speed, params.v_min, params.v_max, params.format, params.slider_flags
            )
        elif params.edit_type == IntEditType.knob:
            changed, r.value = imgui_knobs.knob_int(
                params.label,
                r.value,
                params.v_min,
                params.v_max,
                params.knob_speed,
                params.format,
                params.knob_variant,
                hello_imgui.em_size(params.knob_size_em),
                params.knob_steps,
            )

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


def make_int_source(initial_value: int, params: IntEditParams | None = None, label: str = "Source") -> SourceWithGui:
    x = make_int_with_gui(initial_value, params)
    return SourceWithGui(x, label)


########################################################################################################################
#                               Floats
########################################################################################################################
class FloatEditType(Enum):
    slider = 1
    input = 2
    drag = 3
    knob = 4


@dataclass
class FloatEditParams:
    label: str = "##float"
    v_min: float = 0.0
    v_max: float = 10.0
    format: str = "%.3f"
    width_em: float = 10
    edit_type: FloatEditType = FloatEditType.slider
    # Specific to slider_float
    slider_flags: int = imgui.SliderFlags_.none.value
    # Specific to input_float
    input_step: float = 0.0
    input_step_fast: float = 0.0
    input_flags: int = imgui.InputTextFlags_.none.value
    # Specific to drag_float
    v_speed: float = 1.0
    # Specific to knob
    knob_speed: float = 0.0
    knob_variant: int = imgui_knobs.ImGuiKnobVariant_.tick.value
    knob_size_em: float = 2.5
    knob_steps: int = 0


def make_float_with_gui(initial_value: float, params: FloatEditParams | None = None) -> AnyDataWithGui:
    if params is None:
        params = FloatEditParams()
    r = AnyDataWithGui()
    r.value = initial_value
    r.gui_present_impl = lambda: _present_str(r.value)
    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
        if params.edit_type == FloatEditType.slider:
            changed, r.value = imgui.slider_float(
                params.label, r.value, params.v_min, params.v_max, params.format, params.slider_flags
            )
        elif params.edit_type == FloatEditType.input:
            changed, r.value = imgui.input_float(
                params.label, r.value, params.input_step, params.input_step_fast, params.format, params.input_flags
            )
        elif params.edit_type == FloatEditType.drag:
            changed, r.value = imgui.drag_float(
                params.label, r.value, params.v_speed, params.v_min, params.v_max, params.format, params.slider_flags
            )
        elif params.edit_type == FloatEditType.knob:
            changed, r.value = imgui_knobs.knob(
                params.label,
                r.value,
                params.v_min,
                params.v_max,
                params.knob_speed,
                params.format,
                params.knob_variant,
                hello_imgui.em_size(params.knob_size_em),
                params.knob_steps,
            )

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


def make_float_source(
    initial_value: float, params: FloatEditParams | None = None, label: str = "Source"
) -> SourceWithGui:
    x = make_float_with_gui(initial_value, params)
    return SourceWithGui(x, label)


########################################################################################################################
#                               Bool
########################################################################################################################
class BoolEditType(Enum):
    checkbox = 1
    radio_button = 2
    toggle = 3


class BoolEditParams:
    label: str = "##bool"
    edit_type: BoolEditType = BoolEditType.checkbox
    # Specific to toggle
    toggle_config: ToggleConfig | None = None


def make_bool_with_gui(initial_value: bool, params: BoolEditParams | None = None) -> AnyDataWithGui:
    if params is None:
        params = BoolEditParams()
    r = AnyDataWithGui()
    r.value = initial_value
    r.gui_present_impl = lambda: _present_str(r.value)
    first_frame = True

    def edit() -> bool:
        assert params is not None
        nonlocal first_frame
        changed = False
        if params.edit_type == BoolEditType.checkbox:
            changed, r.value = imgui.checkbox(params.label, r.value)
        elif params.edit_type == BoolEditType.radio_button:
            new_value = imgui.radio_button(params.label, r.value)
            if new_value != r.value:
                r.value = new_value
                changed = True
        elif params.edit_type == BoolEditType.toggle:
            if params.toggle_config is None:
                raise ValueError("toggle_config must be set for BoolEditType.toggle")
            changed, r.value = imgui_toggle.toggle(params.label, r.value, params.toggle_config)

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


########################################################################################################################
#                               Str
########################################################################################################################
class StrEditType(Enum):
    input = 1
    input_with_hint = 2
    multiline = 3


@dataclass
class StrEditParams:
    label: str = "##str"
    edit_type: StrEditType = StrEditType.input
    input_flags: int = imgui.InputTextFlags_.none.value
    width_em: float = 10  # if 0, then use all available width
    # Callbacks
    callback: Callable[[imgui.InputTextCallbackData], int] = None  # type: ignore
    user_data: Any | None = None
    # Specific to input_with_hint
    hint: str = ""
    # Specific to multiline
    height_em: int = 5


def make_str_with_gui(initial_value: str, params: StrEditParams | None = None) -> AnyDataWithGui:
    if params is None:
        params = StrEditParams()
    r = AnyDataWithGui()
    r.value = initial_value
    r.gui_present_impl = lambda: _present_str(r.value)
    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
        if params.edit_type == StrEditType.input:
            changed, r.value = imgui.input_text(
                params.label, r.value, params.input_flags, params.callback, params.user_data
            )
        elif params.edit_type == StrEditType.input_with_hint:
            changed, r.value = imgui.input_text_with_hint(
                params.label, params.hint, r.value, params.input_flags, params.callback, params.user_data
            )
        elif params.edit_type == StrEditType.multiline:
            size = hello_imgui.em_to_vec2(params.width_em, params.height_em)
            changed, r.value = imgui.input_text_multiline(
                params.label, r.value, size, params.input_flags, params.callback, params.user_data
            )

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


def make_str_source(initial_value: str, params: StrEditParams | None = None, label: str = "Source") -> SourceWithGui:
    x = make_str_with_gui(initial_value, params)
    return SourceWithGui(x, label)


########################################################################################################################
#                               __all__
########################################################################################################################

__all__ = [
    # Ints
    "IntEditParams",
    "IntEditType",
    "make_int_with_gui",
    "make_int_source",
    # Floats
    "FloatEditParams",
    "FloatEditType",
    "make_float_with_gui",
    "make_float_source",
    "ImGuiKnobVariant_",
    # Str
    "StrEditParams",
    "StrEditType",
    "make_str_with_gui",
    "make_str_source",
    # Bool
    "ToggleConfig",
]
