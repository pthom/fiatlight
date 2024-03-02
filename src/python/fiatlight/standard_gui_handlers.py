from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, imgui_ctx
from imgui_bundle import icons_fontawesome
from fiatlight.fiatlight_types import UnspecifiedValue, ErrorValue
from fiatlight.any_data_with_gui import AnyDataGuiHandlers, DataType
from fiatlight.internal import osd_widgets

from typing import Any, Callable, TypeAlias, Tuple
from dataclasses import dataclass
from enum import Enum
import copy


########################################################################################################################
#                               _versatile_gui_present
########################################################################################################################
def versatile_gui_present(value: Any) -> None:
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
    elif value is UnspecifiedValue:
        imgui.text("Unspecified")
    elif value is ErrorValue:
        imgui.text("Error")
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
                        versatile_gui_present(v)

                _add_details_button(value, detail_gui)
                break
            else:
                versatile_gui_present(v)
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
class IntWithGuiParams:
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


def make_int_gui_handlers(params: IntWithGuiParams | None = None) -> AnyDataGuiHandlers[int]:
    _params = params if params is not None else IntWithGuiParams()

    def edit(x: int) -> Tuple[bool, int]:
        assert isinstance(x, int)
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(_params.width_em))
        if _params.edit_type == IntEditType.slider:
            changed, x = imgui.slider_int(
                _params.label,
                x,
                _params.v_min,
                _params.v_max,
                _params.format,
                _params.slider_flags,
            )
        elif _params.edit_type == IntEditType.input:
            changed, x = imgui.input_int(
                _params.label, x, _params.input_step, _params.input_step_fast, _params.input_flags
            )
        elif _params.edit_type == IntEditType.drag:
            changed, x = imgui.drag_int(
                _params.label,
                x,
                _params.v_speed,
                _params.v_min,
                _params.v_max,
                _params.format,
                _params.slider_flags,
            )
        elif _params.edit_type == IntEditType.knob:
            changed, x = imgui_knobs.knob_int(
                _params.label,
                x,
                _params.v_min,
                _params.v_max,
                _params.knob_speed,
                _params.format,
                _params.knob_variant,
                hello_imgui.em_size(_params.knob_size_em),
                _params.knob_steps,
            )

        return changed, x

    r = AnyDataGuiHandlers[int]()
    r.gui_edit_impl = edit
    r.default_value_provider = lambda: 0
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
class FloatWithGuiParams:
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


def make_float_gui_handlers(params: FloatWithGuiParams | None = None) -> AnyDataGuiHandlers[float]:
    if params is None:
        params = FloatWithGuiParams()

    def edit(x: float) -> Tuple[bool, float]:
        assert isinstance(x, float)
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
        if params.edit_type == FloatEditType.slider:
            changed, x = imgui.slider_float(
                params.label,
                x,
                params.v_min,
                params.v_max,
                params.format,
                params.slider_flags,
            )
        elif params.edit_type == FloatEditType.input:
            changed, x = imgui.input_float(
                params.label,
                x,
                params.input_step,
                params.input_step_fast,
                params.format,
                params.input_flags,
            )
        elif params.edit_type == FloatEditType.drag:
            changed, x = imgui.drag_float(
                params.label,
                x,
                params.v_speed,
                params.v_min,
                params.v_max,
                params.format,
                params.slider_flags,
            )
        elif params.edit_type == FloatEditType.knob:
            changed, x = imgui_knobs.knob(
                params.label,
                x,
                params.v_min,
                params.v_max,
                params.knob_speed,
                params.format,
                params.knob_variant,
                hello_imgui.em_size(params.knob_size_em),
                params.knob_steps,
            )

        return changed, x

    r = AnyDataGuiHandlers[float]()
    r.gui_edit_impl = edit
    r.default_value_provider = lambda: 0.0
    return r


########################################################################################################################
#                               Bool
########################################################################################################################
class BoolEditType(Enum):
    checkbox = 1
    radio_button = 2
    toggle = 3


@dataclass
class BoolWithGuiParams:
    default_edit_value = False
    label: str = "##bool"
    edit_type: BoolEditType = BoolEditType.checkbox
    # Specific to toggle
    toggle_config: ToggleConfig | None = None


def make_bool_gui_handlers(params: BoolWithGuiParams | None = None) -> AnyDataGuiHandlers[bool]:
    if params is None:
        params = BoolWithGuiParams()

    def edit(x: bool) -> Tuple[bool, bool]:
        assert params is not None
        assert isinstance(x, bool)
        changed = False
        if params.edit_type == BoolEditType.checkbox:
            changed, x = imgui.checkbox(params.label, x)
        elif params.edit_type == BoolEditType.radio_button:
            new_x = imgui.radio_button(params.label, x)
            if new_x != x:
                x = new_x
                changed = True
        elif params.edit_type == BoolEditType.toggle:
            if params.toggle_config is None:
                raise ValueError("toggle_config must be set for BoolEditType.toggle")
            changed, x = imgui_toggle.toggle(params.label, x, params.toggle_config)

        return changed, x

    r = AnyDataGuiHandlers[bool]()
    r.gui_edit_impl = edit
    r.default_value_provider = lambda: False
    return r


########################################################################################################################
#                               Str
########################################################################################################################
class StrEditType(Enum):
    input = 1
    input_with_hint = 2
    multiline = 3


@dataclass
class StrWithGuiParams:
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


def make_str_gui_handlers(params: StrWithGuiParams | None = None) -> AnyDataGuiHandlers[str]:
    if params is None:
        params = StrWithGuiParams()

    def edit(x: str) -> Tuple[bool, str]:
        assert isinstance(x, str)
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(params.width_em))
        if params.edit_type == StrEditType.input:
            changed, x = imgui.input_text(params.label, x, params.input_flags, params.callback, params.user_data)
        elif params.edit_type == StrEditType.input_with_hint:
            changed, x = imgui.input_text_with_hint(
                params.label,
                params.hint,
                x,
                params.input_flags,
                params.callback,
                params.user_data,
            )
        elif params.edit_type == StrEditType.multiline:
            size = hello_imgui.em_to_vec2(params.width_em, params.height_em)
            changed, x = imgui.input_text_multiline(
                params.label, x, size, params.input_flags, params.callback, params.user_data
            )

        return changed, x

    r = AnyDataGuiHandlers[str]()
    r.gui_edit_impl = edit
    r.default_value_provider = lambda: ""
    return r


########################################################################################################################
#                               List Handlers
########################################################################################################################
def make_list_gui_handlers(item_gui_handlers: AnyDataGuiHandlers[DataType]) -> AnyDataGuiHandlers[list[DataType]]:
    def edit(x: list[Any]) -> Tuple[bool, list[Any]]:
        assert isinstance(x, list)
        item_gui_edit_impl = item_gui_handlers.gui_edit_impl
        default_value_provider = item_gui_handlers.default_value_provider

        if item_gui_edit_impl is None:
            return False, x
        changed = False
        new_x = x
        imgui.new_line()
        for i, item in enumerate(x):
            imgui.push_id(str(i))
            changed_i, new_item = item_gui_edit_impl(item)
            if changed_i:
                changed = True
                x[i] = new_item

            imgui.same_line()
            if imgui.small_button(icons_fontawesome.ICON_FA_MINUS):
                new_x = copy.copy(x)
                new_x.pop(i)
                changed = True

            if default_value_provider is not None:
                imgui.same_line()
                if imgui.button(icons_fontawesome.ICON_FA_PLUS):
                    new_x = copy.copy(x)
                    new_x.insert(i, default_value_provider())
                    changed = True

            imgui.pop_id()

        if default_value_provider is not None:
            if imgui.button(icons_fontawesome.ICON_FA_PLUS):
                new_x = copy.copy(x)
                new_x.append(default_value_provider())
                changed = True

        return changed, new_x

    # def present(x: list[Any]) -> None:
    #     for i, item in enumerate(x):
    #         item_gui_handlers.gui_present_impl(item)

    r = AnyDataGuiHandlers[list[Any]]()
    r.gui_edit_impl = edit
    r.default_value_provider = lambda: []

    # item_to_dict_impl = item_gui_handlers.to_dict_impl
    # item_from_dict_impl = item_gui_handlers.from_dict_impl
    # if item_to_dict_impl is not None and item_from_dict_impl is not None:
    #     r.to_dict_impl = lambda x: {"values": [item_to_dict_impl(item) for item in x]}
    #     r.from_dict_impl = lambda d: [item_from_dict_impl(item_dict) for item_dict in d["values"]]
    # else:
    #     r.to_dict_impl = lambda x: {"values": x}
    #     r.from_dict_impl = lambda d: d["values"]

    return r


########################################################################################################################
#                               __all__
########################################################################################################################

__all__ = [
    # Ints
    "IntWithGuiParams",
    "IntEditType",
    "make_int_gui_handlers",
    # Floats
    "FloatWithGuiParams",
    "FloatEditType",
    "make_float_gui_handlers",
    "ImGuiKnobVariant_",
    # Str
    "StrWithGuiParams",
    "StrEditType",
    "make_str_gui_handlers",
    # Bool
    "ToggleConfig",
    "BoolWithGuiParams",
    "BoolEditType",
    "make_bool_gui_handlers",
]


########################################################################################################################
#                              sandbox
########################################################################################################################
