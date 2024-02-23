from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, imgui_ctx
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import SourceWithGui
from fiatlight.internal import osd_widgets

from typing import Any, Callable, TypeAlias, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum


########################################################################################################################
#                               AnyDataParams
########################################################################################################################

# class AnyDataEditParams:
#     pass

# class AnyDataPresentParams:
#     pass


AnyDataEditParams = TypeVar("AnyDataEditParams")
AnyDataPresentParams = TypeVar("AnyDataPresentParams")


class NoDataEditParams:
    pass


class NoDataPresentParams:
    pass


@dataclass
class AnyDataParams(Generic[AnyDataEditParams, AnyDataPresentParams]):
    edit_params: AnyDataEditParams | None = None
    present_params: AnyDataPresentParams | None = None


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
        imgui.text(f"Int Value={value}")
    elif isinstance(value, float):
        imgui.text(f"Float Value={value:.4f}")
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


def make_int_with_gui(
    initial_value: int | None = None,
    edit_params: IntEditParams | None = None,
    present_params: NoDataPresentParams | None = None,
) -> AnyDataWithGui:
    if edit_params is None:
        edit_params = IntEditParams()
    r = AnyDataWithGui()
    r.value = initial_value

    if isinstance(present_params, NoDataPresentParams):
        r.gui_present_impl = lambda: _versatile_gui_present(r.value)
    else:
        assert False  # Not implemented!

    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(edit_params.width_em))
        if edit_params.edit_type == IntEditType.slider:
            changed, r.value = imgui.slider_int(
                edit_params.label,
                r.value,
                edit_params.v_min,
                edit_params.v_max,
                edit_params.format,
                edit_params.slider_flags,
            )
        elif edit_params.edit_type == IntEditType.input:
            changed, r.value = imgui.input_int(
                edit_params.label, r.value, edit_params.input_step, edit_params.input_step_fast, edit_params.input_flags
            )
        elif edit_params.edit_type == IntEditType.drag:
            changed, r.value = imgui.drag_int(
                edit_params.label,
                r.value,
                edit_params.v_speed,
                edit_params.v_min,
                edit_params.v_max,
                edit_params.format,
                edit_params.slider_flags,
            )
        elif edit_params.edit_type == IntEditType.knob:
            changed, r.value = imgui_knobs.knob_int(
                edit_params.label,
                r.value,
                edit_params.v_min,
                edit_params.v_max,
                edit_params.knob_speed,
                edit_params.format,
                edit_params.knob_variant,
                hello_imgui.em_size(edit_params.knob_size_em),
                edit_params.knob_steps,
            )

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


def make_int_source(
    initial_value: int, edit_params: IntEditParams | None = None, label: str = "Source"
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


def make_float_with_gui(
    initial_value: float | None = None,
    edit_params: FloatEditParams | None = None,
    present_params: NoDataPresentParams | None = None,
) -> AnyDataWithGui:
    if edit_params is None:
        edit_params = FloatEditParams()
    r = AnyDataWithGui()
    r.value = initial_value

    if isinstance(present_params, NoDataPresentParams):
        r.gui_present_impl = lambda: _versatile_gui_present(r.value)
    else:
        assert False  # Not implemented!

    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(edit_params.width_em))
        if edit_params.edit_type == FloatEditType.slider:
            changed, r.value = imgui.slider_float(
                edit_params.label,
                r.value,
                edit_params.v_min,
                edit_params.v_max,
                edit_params.format,
                edit_params.slider_flags,
            )
        elif edit_params.edit_type == FloatEditType.input:
            changed, r.value = imgui.input_float(
                edit_params.label,
                r.value,
                edit_params.input_step,
                edit_params.input_step_fast,
                edit_params.format,
                edit_params.input_flags,
            )
        elif edit_params.edit_type == FloatEditType.drag:
            changed, r.value = imgui.drag_float(
                edit_params.label,
                r.value,
                edit_params.v_speed,
                edit_params.v_min,
                edit_params.v_max,
                edit_params.format,
                edit_params.slider_flags,
            )
        elif edit_params.edit_type == FloatEditType.knob:
            changed, r.value = imgui_knobs.knob(
                edit_params.label,
                r.value,
                edit_params.v_min,
                edit_params.v_max,
                edit_params.knob_speed,
                edit_params.format,
                edit_params.knob_variant,
                hello_imgui.em_size(edit_params.knob_size_em),
                edit_params.knob_steps,
            )

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


def make_float_source(
    initial_value: float, edit_params: FloatEditParams | None = None, label: str = "Source"
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
class BoolEditParams:
    label: str = "##bool"
    edit_type: BoolEditType = BoolEditType.checkbox
    # Specific to toggle
    toggle_config: ToggleConfig | None = None


def make_bool_with_gui(
    initial_value: bool | None = None,
    edit_params: BoolEditParams | None = None,
    present_params: NoDataPresentParams | None = None,
) -> AnyDataWithGui:
    if edit_params is None:
        edit_params = BoolEditParams()
    r = AnyDataWithGui()
    r.value = initial_value

    if isinstance(present_params, NoDataPresentParams):
        r.gui_present_impl = lambda: _versatile_gui_present(r.value)
    else:
        assert False  # Not implemented!

    first_frame = True

    def edit() -> bool:
        assert edit_params is not None
        nonlocal first_frame
        changed = False
        if edit_params.edit_type == BoolEditType.checkbox:
            changed, r.value = imgui.checkbox(edit_params.label, r.value)
        elif edit_params.edit_type == BoolEditType.radio_button:
            new_value = imgui.radio_button(edit_params.label, r.value)
            if new_value != r.value:
                r.value = new_value
                changed = True
        elif edit_params.edit_type == BoolEditType.toggle:
            if edit_params.toggle_config is None:
                raise ValueError("toggle_config must be set for BoolEditType.toggle")
            changed, r.value = imgui_toggle.toggle(edit_params.label, r.value, edit_params.toggle_config)

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


def make_str_with_gui(
    initial_value: str | None = None,
    edit_params: StrEditParams | None = None,
    present_params: NoDataPresentParams | None = None,
) -> AnyDataWithGui:
    if edit_params is None:
        edit_params = StrEditParams()
    r = AnyDataWithGui()
    r.value = initial_value

    if isinstance(present_params, NoDataPresentParams):
        r.gui_present_impl = lambda: _versatile_gui_present(r.value)
    else:
        assert False  # Not implemented!

    first_frame = True

    def edit() -> bool:
        nonlocal first_frame
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(edit_params.width_em))
        if edit_params.edit_type == StrEditType.input:
            changed, r.value = imgui.input_text(
                edit_params.label, r.value, edit_params.input_flags, edit_params.callback, edit_params.user_data
            )
        elif edit_params.edit_type == StrEditType.input_with_hint:
            changed, r.value = imgui.input_text_with_hint(
                edit_params.label,
                edit_params.hint,
                r.value,
                edit_params.input_flags,
                edit_params.callback,
                edit_params.user_data,
            )
        elif edit_params.edit_type == StrEditType.multiline:
            size = hello_imgui.em_to_vec2(edit_params.width_em, edit_params.height_em)
            changed, r.value = imgui.input_text_multiline(
                edit_params.label, r.value, size, edit_params.input_flags, edit_params.callback, edit_params.user_data
            )

        if first_frame:
            changed = True
            first_frame = False

        return changed

    r.gui_edit_impl = edit

    return r


def make_str_source(
    initial_value: str, edit_params: StrEditParams | None = None, label: str = "Source"
) -> SourceWithGui:
    x = make_str_with_gui(initial_value, edit_params)
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
