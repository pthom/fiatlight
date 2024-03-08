from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle
from fiatlight.core import UnspecifiedValue, ErrorValue, DataType, AnyDataWithGui, AnyDataGuiCallbacks
from typing import Any, Callable, TypeAlias, Tuple
from dataclasses import dataclass
from enum import Enum
import copy


GuiFunction = Callable[[], None]

########################################################################################################################
#                               _versatile_gui_present
########################################################################################################################


def versatile_gui_present(value: Any) -> None:
    from fiatlight.widgets.text_custom import present_expandable_str
    from fiatlight.widgets import osd_widgets

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
        imgui.text(f"str len={len(value)}")
        max_len = 30
        if len(value) < max_len:
            imgui.text('"' + value + '"')
        else:
            present_expandable_str(value[:max_len], value)
    elif isinstance(value, list):
        value_full_str = "\n".join(str(item) for item in value)
        imgui.text(f"list len={len(value)}")
        max_len = 10
        if len(value) < max_len:
            imgui.text(value_full_str)
        else:
            value_extract_str = "\n".join(str(item) for item in value[:max_len])
            present_expandable_str(value_extract_str, value_full_str)
    elif isinstance(value, tuple):
        imgui.text(f"Tuple len={len(value)}")
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


class IntWithGui(AnyDataWithGui[int]):
    params: IntWithGuiParams

    def __init__(self, params: IntWithGuiParams | None = None) -> None:
        super().__init__()
        self.params = params if params is not None else IntWithGuiParams()

        def edit(x: int) -> Tuple[bool, int]:
            assert isinstance(x, int)
            changed = False
            imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
            if self.params.edit_type == IntEditType.slider:
                changed, x = imgui.slider_int(
                    self.params.label,
                    x,
                    self.params.v_min,
                    self.params.v_max,
                    self.params.format,
                    self.params.slider_flags,
                )
            elif self.params.edit_type == IntEditType.input:
                changed, x = imgui.input_int(
                    self.params.label, x, self.params.input_step, self.params.input_step_fast, self.params.input_flags
                )
            elif self.params.edit_type == IntEditType.drag:
                changed, x = imgui.drag_int(
                    self.params.label,
                    x,
                    self.params.v_speed,
                    self.params.v_min,
                    self.params.v_max,
                    self.params.format,
                    self.params.slider_flags,
                )
            elif self.params.edit_type == IntEditType.knob:
                changed, x = imgui_knobs.knob_int(
                    self.params.label,
                    x,
                    self.params.v_min,
                    self.params.v_max,
                    self.params.knob_speed,
                    self.params.format,
                    self.params.knob_variant,
                    hello_imgui.em_size(self.params.knob_size_em),
                    self.params.knob_steps,
                )
            return changed, x

        self.callbacks.edit = edit
        self.callbacks.default_value_provider = lambda: 0


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


class FloatWithGui(AnyDataWithGui[float]):
    params: FloatWithGuiParams

    def __init__(self, params: FloatWithGuiParams | None = None) -> None:
        super().__init__()
        self.params = params if params is not None else FloatWithGuiParams()

        def edit(x: float) -> Tuple[bool, float]:
            assert isinstance(x, float)
            changed = False
            imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
            if self.params.edit_type == FloatEditType.slider:
                changed, x = imgui.slider_float(
                    self.params.label,
                    x,
                    self.params.v_min,
                    self.params.v_max,
                    self.params.format,
                    self.params.slider_flags,
                )
            elif self.params.edit_type == FloatEditType.input:
                changed, x = imgui.input_float(
                    self.params.label,
                    x,
                    self.params.input_step,
                    self.params.input_step_fast,
                    self.params.format,
                    self.params.input_flags,
                )
            elif self.params.edit_type == FloatEditType.drag:
                changed, x = imgui.drag_float(
                    self.params.label,
                    x,
                    self.params.v_speed,
                    self.params.v_min,
                    self.params.v_max,
                    self.params.format,
                    self.params.slider_flags,
                )
            elif self.params.edit_type == FloatEditType.knob:
                changed, x = imgui_knobs.knob(
                    self.params.label,
                    x,
                    self.params.v_min,
                    self.params.v_max,
                    self.params.knob_speed,
                    self.params.format,
                    self.params.knob_variant,
                    hello_imgui.em_size(self.params.knob_size_em),
                    self.params.knob_steps,
                )

            return changed, x

        self.callbacks.edit = edit
        self.callbacks.default_value_provider = lambda: 0.0


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


class BoolWithGui(AnyDataWithGui[bool]):
    params: BoolWithGuiParams

    def __init__(self, params: BoolWithGuiParams | None = None):
        super().__init__()
        self.params = params if params is not None else BoolWithGuiParams()

        def edit(x: bool) -> Tuple[bool, bool]:
            assert isinstance(x, bool)
            changed = False
            if self.params.edit_type == BoolEditType.checkbox:
                changed, x = imgui.checkbox(self.params.label, x)
            elif self.params.edit_type == BoolEditType.radio_button:
                new_x = imgui.radio_button(self.params.label, x)
                if new_x != x:
                    x = new_x
                    changed = True
            elif self.params.edit_type == BoolEditType.toggle:
                if self.params.toggle_config is None:
                    raise ValueError("toggle_config must be set for BoolEditType.toggle")
                changed, x = imgui_toggle.toggle(self.params.label, x, self.params.toggle_config)

            return changed, x

        self.callbacks.edit = edit
        self.callbacks.default_value_provider = lambda: False


########################################################################################################################
#                               Str
########################################################################################################################
class StrEditType(Enum):
    input = 1
    input_with_hint = 2
    multiline = 3  # multiline text input does *not* work inside a Node


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


class StrWithGui(AnyDataWithGui[str]):
    params: StrWithGuiParams

    def __init__(self, params: StrWithGuiParams | None = None) -> None:
        super().__init__()
        self.params = params if params is not None else StrWithGuiParams()

        def edit(x: str) -> Tuple[bool, str]:
            assert isinstance(x, str)
            changed = False
            imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
            if self.params.edit_type == StrEditType.input:
                changed, x = imgui.input_text(
                    self.params.label, x, self.params.input_flags, self.params.callback, self.params.user_data
                )
            elif self.params.edit_type == StrEditType.input_with_hint:
                changed, x = imgui.input_text_with_hint(
                    self.params.label,
                    self.params.hint,
                    x,
                    self.params.input_flags,
                    self.params.callback,
                    self.params.user_data,
                )
            elif self.params.edit_type == StrEditType.multiline:
                size = hello_imgui.em_to_vec2(self.params.width_em, self.params.height_em)
                changed, x = imgui.input_text_multiline(
                    self.params.label, x, size, self.params.input_flags, self.params.callback, self.params.user_data
                )

            return changed, x

        self.callbacks.edit = edit
        self.callbacks.default_value_provider = lambda: ""


########################################################################################################################
#                               List Handlers
########################################################################################################################
class ListWithGui(AnyDataWithGui[list[DataType]]):
    item_gui_handlers: AnyDataGuiCallbacks[DataType]

    def __init__(self, item_gui_handlers: AnyDataGuiCallbacks[DataType]) -> None:
        super().__init__()
        self.item_gui_handlers = item_gui_handlers
        self.callbacks.edit = lambda x: self.edit(x)
        self.callbacks.default_value_provider = lambda: []
        # def present(x: list[Any]) -> None:
        #     for i, item in enumerate(x):
        #         item_gui_handlers.present(item)

        # item_to_dict_impl = item_gui_handlers.to_dict_impl
        # item_from_dict_impl = item_gui_handlers.from_dict_impl
        # if item_to_dict_impl is not None and item_from_dict_impl is not None:
        #     r.to_dict_impl = lambda x: {"values": [item_to_dict_impl(item) for item in x]}
        #     r.from_dict_impl = lambda d: [item_from_dict_impl(item_dict) for item_dict in d["values"]]
        # else:
        #     r.to_dict_impl = lambda x: {"values": x}
        #     r.from_dict_impl = lambda d: d["values"]

    def edit(self, x: list[Any]) -> Tuple[bool, list[Any]]:
        from fiatlight.widgets import IconsFontAwesome6

        assert isinstance(x, list)
        item_gui_edit_impl = self.item_gui_handlers.edit
        default_value_provider = self.item_gui_handlers.default_value_provider

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
            if imgui.small_button(IconsFontAwesome6.ICON_MINUS):
                new_x = copy.copy(x)
                new_x.pop(i)
                changed = True

            if default_value_provider is not None:
                imgui.same_line()
                if imgui.button(IconsFontAwesome6.ICON_PLUS):
                    new_x = copy.copy(x)
                    new_x.insert(i, default_value_provider())
                    changed = True

            imgui.pop_id()

        if default_value_provider is not None:
            if imgui.button(IconsFontAwesome6.ICON_PLUS):
                new_x = copy.copy(x)
                new_x.append(default_value_provider())
                changed = True

        return changed, new_x


########################################################################################################################
#                               __all__
########################################################################################################################

__all__ = [
    # Ints
    "IntWithGuiParams",
    "IntEditType",
    "IntWithGui",
    # Floats
    "FloatWithGuiParams",
    "FloatEditType",
    "FloatWithGui",
    "ImGuiKnobVariant_",
    # Str
    "StrWithGuiParams",
    "StrEditType",
    "StrWithGui",
    # Bool
    "ToggleConfig",
    "BoolWithGuiParams",
    "BoolEditType",
    "BoolWithGui",
    # List
    "ListWithGui",
    # Versatile present
    "versatile_gui_present",
]


########################################################################################################################
#                              sandbox
########################################################################################################################
