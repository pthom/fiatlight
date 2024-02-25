from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, imgui_ctx
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import SourceWithGui
from fiatlight.to_gui import DataWithGuiParamsBase
from fiatlight.internal import osd_widgets

from typing import Any, Callable, TypeAlias
from dataclasses import dataclass
from enum import Enum


########################################################################################################################
#                               _versatile_gui_present
########################################################################################################################
def _versatile_gui_present(value: Any) -> None:
    def _add_details_button(obj: Any, detail_gui: Callable[[], None]) -> None:
        with imgui_ctx.push_obj_id(obj):
            if imgui.button("show details"):
                osd_widgets.set_detail_gui(detail_gui)
            if imgui.is_item_hovered():
                osd_widgets.set_tooltip(
                    "Click to show details, then open the Info tab at the bottom to see the full string"
                )

    if value is None:
        imgui.text("None")
    elif isinstance(value, int):
        imgui.text(f"{value}")
    elif isinstance(value, float):
        imgui.text(f"{value:.4f}")
        if imgui.is_item_hovered():
            osd_widgets.set_tooltip(f"{value}")
    elif isinstance(value, str):
        max_len = 30
        if len(value) > max_len:
            imgui.text(f"Str len={len(value)}")
            imgui.text('"' + value[:max_len])

            def detail_gui() -> None:
                imgui.input_text_multiline("##value_text", value)

            _add_details_button(value, detail_gui)
            if imgui.is_item_hovered():
                osd_widgets.set_tooltip(
                    "Click to show details, then open the Info tab at the bottom to see the full string"
                )
        else:
            imgui.text('"' + value + '"')
    elif isinstance(value, list):
        imgui.text(f"List len={len(value)}")
        for i, v in enumerate(value):
            if i >= 5:

                def detail_gui() -> None:
                    for i, v in enumerate(value):
                        _versatile_gui_present(v)

                _add_details_button(value, detail_gui)
                break
            else:
                _versatile_gui_present(v)
    elif isinstance(value, tuple):
        # imgui.text(f"Tuple len={len(value)}")
        strs = [str(v) for v in value]
        tuple_str = "(" + ", ".join(strs) + ")"
        imgui.text(tuple_str)

    else:
        raise Exception(f"versatile_gui_data Unsupported type: {type(value)}")


########################################################################################################################
#                               Ints
########################################################################################################################
ImGuiKnobVariant_: TypeAlias = imgui_knobs.ImGuiKnobVariant_
ToggleConfig: TypeAlias = imgui_toggle.ToggleConfig


class IntEditType(Enum):
    slider = 1
    input = 2
    drag = 3
    knob = 4


@dataclass
class IntWithGuiParams(DataWithGuiParamsBase[int]):
    default_edit_value = 0
    #
    edit_type: IntEditType = IntEditType.slider
    # Common
    label: str = "##int"
    v_min: int = 0
    v_max: int = 10
    width_em: float = 6
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


def make_int_with_gui(
    initial_value: int | None = None,
    params: IntWithGuiParams | None = None,
) -> AnyDataWithGui:
    if params is None:
        params = IntWithGuiParams()
    r = AnyDataWithGui()
    r.value = initial_value

    r.gui_present_impl = lambda: _versatile_gui_present(r.value)

    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
        if params.edit_type == IntEditType.slider:
            changed, r.value = imgui.slider_int(
                params.label,
                r.value,
                params.v_min,
                params.v_max,
                params.format,
                params.slider_flags,
            )
        elif params.edit_type == IntEditType.input:
            changed, r.value = imgui.input_int(
                params.label, r.value, params.input_step, params.input_step_fast, params.input_flags
            )
        elif params.edit_type == IntEditType.drag:
            changed, r.value = imgui.drag_int(
                params.label,
                r.value,
                params.v_speed,
                params.v_min,
                params.v_max,
                params.format,
                params.slider_flags,
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

    r.gui_edit_impl = lambda: params.edit_handle_none(r, edit)

    r.to_dict = lambda x: {"value": x}
    r.from_dict = lambda x: x["value"]

    return r


def make_int_source(
    initial_value: int, edit_params: IntWithGuiParams | None = None, label: str = "Source"
) -> SourceWithGui:
    x = make_int_with_gui(initial_value, edit_params)
    r = SourceWithGui(x, label)
    return r


########################################################################################################################
#                               Floats
########################################################################################################################
class FloatEditType(Enum):
    slider = 1
    input = 2
    drag = 3
    knob = 4


@dataclass
class FloatWithGuiParams(DataWithGuiParamsBase[float]):
    default_edit_value = 0.0
    label: str = "##float"
    v_min: float = 0.0
    v_max: float = 10.0
    format: str = "%.3f"
    width_em: float = 6
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


def make_float_with_gui(initial_value: float | None = None, params: FloatWithGuiParams | None = None) -> AnyDataWithGui:
    if params is None:
        params = FloatWithGuiParams()
    r = AnyDataWithGui()
    r.value = initial_value

    r.gui_present_impl = lambda: _versatile_gui_present(r.value)

    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
        if params.edit_type == FloatEditType.slider:
            changed, r.value = imgui.slider_float(
                params.label,
                r.value,
                params.v_min,
                params.v_max,
                params.format,
                params.slider_flags,
            )
        elif params.edit_type == FloatEditType.input:
            changed, r.value = imgui.input_float(
                params.label,
                r.value,
                params.input_step,
                params.input_step_fast,
                params.format,
                params.input_flags,
            )
        elif params.edit_type == FloatEditType.drag:
            changed, r.value = imgui.drag_float(
                params.label,
                r.value,
                params.v_speed,
                params.v_min,
                params.v_max,
                params.format,
                params.slider_flags,
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

    r.gui_edit_impl = lambda: params.edit_handle_none(r, edit)

    return r


def make_float_source(
    initial_value: float, edit_params: FloatWithGuiParams | None = None, label: str = "Source"
) -> SourceWithGui:
    x = make_float_with_gui(initial_value, edit_params)
    return SourceWithGui(x, label)


########################################################################################################################
#                               Bool
########################################################################################################################
class BoolEditType(Enum):
    checkbox = 1
    radio_button = 2
    toggle = 3


@dataclass
class BoolWithGuiParams(DataWithGuiParamsBase[bool]):
    default_edit_value = False
    label: str = "##bool"
    edit_type: BoolEditType = BoolEditType.checkbox
    # Specific to toggle
    toggle_config: ToggleConfig | None = None


def make_bool_with_gui(
    initial_value: bool | None = None,
    params: BoolWithGuiParams | None = None,
) -> AnyDataWithGui:
    if params is None:
        params = BoolWithGuiParams()
    r = AnyDataWithGui()
    r.value = initial_value

    r.gui_present_impl = lambda: _versatile_gui_present(r.value)

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

    r.gui_edit_impl = lambda: params.edit_handle_none(r, edit)

    return r


########################################################################################################################
#                               Str
########################################################################################################################
class StrEditType(Enum):
    input = 1
    input_with_hint = 2
    multiline = 3


@dataclass
class StrWithGuiParams(DataWithGuiParamsBase[str]):
    default_edit_value = ""
    label: str = "##str"
    edit_type: StrEditType = StrEditType.input
    input_flags: int = imgui.InputTextFlags_.none.value
    width_em: float = 6  # if 0, then use all available width
    # Callbacks
    callback: Callable[[imgui.InputTextCallbackData], int] = None  # type: ignore
    user_data: Any | None = None
    # Specific to input_with_hint
    hint: str = ""
    # Specific to multiline
    height_em: int = 5


def make_str_with_gui(
    initial_value: str | None = None,
    params: StrWithGuiParams | None = None,
) -> AnyDataWithGui:
    if params is None:
        params = StrWithGuiParams()
    r = AnyDataWithGui()
    r.value = initial_value

    r.gui_present_impl = lambda: _versatile_gui_present(r.value)

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
                params.label,
                params.hint,
                r.value,
                params.input_flags,
                params.callback,
                params.user_data,
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

    r.gui_edit_impl = lambda: params.edit_handle_none(r, edit)

    return r


def make_str_source(
    initial_value: str, edit_params: StrWithGuiParams | None = None, label: str = "Source"
) -> SourceWithGui:
    x = make_str_with_gui(initial_value, edit_params)
    return SourceWithGui(x, label)


########################################################################################################################
#                               __all__
########################################################################################################################

__all__ = [
    # Ints
    "IntWithGuiParams",
    "IntEditType",
    "make_int_with_gui",
    "make_int_source",
    # Floats
    "FloatWithGuiParams",
    "FloatEditType",
    "make_float_with_gui",
    "make_float_source",
    "ImGuiKnobVariant_",
    # Str
    "StrWithGuiParams",
    "StrEditType",
    "make_str_with_gui",
    "make_str_source",
    # Bool
    "ToggleConfig",
]


########################################################################################################################
#                              sandbox
########################################################################################################################
