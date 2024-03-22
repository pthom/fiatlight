import fiatlight.core
from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle
from fiatlight.core import AnyDataWithGui
from typing import Any, Callable, TypeAlias
from dataclasses import dataclass
from enum import Enum


GuiFunction = Callable[[], None]

########################################################################################################################
#                               _versatile_gui_present
########################################################################################################################


# def versatile_gui_present(value: Any) -> None:
#     from fiatlight import widgets
#
#     def show_text(s: str) -> None:
#         widgets.text_maybe_truncated(
#             s,
#             max_width_chars=30,
#             max_lines=10,
#             show_full_as_tooltip=False,
#             show_copy_button=True,
#             show_details_button=True,
#             show_expand_checkbox=True,
#         )
#
#     if value is None:
#         imgui.text("None")
#     elif value is UnspecifiedValue:
#         imgui.text("Unspecified")
#     elif value is ErrorValue:
#         imgui.text("Error")
#     elif isinstance(value, int):
#         imgui.text(f"{value}")
#     elif isinstance(value, float):
#         imgui.text(f"{value:.4f}")
#         if imgui.is_item_hovered():
#             widgets.osd_widgets.set_tooltip(f"{value}")
#     elif isinstance(value, str):
#         imgui.text(f"str len={len(value)}")
#         show_text(value)
#     # elif isinstance(value, list):
#     #     value_full_str = "\n".join(str(item) for item in value)
#     #     imgui.text(f"list len={len(value)}")
#     #     show_text(value_full_str)
#     # elif isinstance(value, tuple):
#     #     imgui.text(f"Tuple len={len(value)}")
#     #     strs = [str(v) for v in value]
#     #     tuple_str = "(" + ", ".join(strs) + ")"
#     #     imgui.text(tuple_str)
#
#     else:
#         raise Exception(f"versatile_gui_data Unsupported type: {type(value)}")


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
    v_max: int = 30
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
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: 0

    def edit(self) -> bool:
        assert isinstance(self.value, int)
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
        if self.params.edit_type == IntEditType.slider:
            changed, self.value = imgui.slider_int(
                self.params.label,
                self.value,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                self.params.slider_flags,
            )
        elif self.params.edit_type == IntEditType.input:
            changed, self.value = imgui.input_int(
                self.params.label,
                self.value,
                self.params.input_step,
                self.params.input_step_fast,
                self.params.input_flags,
            )
        elif self.params.edit_type == IntEditType.drag:
            changed, self.value = imgui.drag_int(
                self.params.label,
                self.value,
                self.params.v_speed,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                self.params.slider_flags,
            )
        elif self.params.edit_type == IntEditType.knob:
            changed, self.value = imgui_knobs.knob_int(
                self.params.label,
                self.value,
                self.params.v_min,
                self.params.v_max,
                self.params.knob_speed,
                self.params.format,
                self.params.knob_variant,
                hello_imgui.em_size(self.params.knob_size_em),
                self.params.knob_steps,
            )
        return changed


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
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: 0.0

    def edit(self) -> bool:
        assert isinstance(self.value, float)
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
        if self.params.edit_type == FloatEditType.slider:
            changed, self.value = imgui.slider_float(
                self.params.label,
                self.value,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                self.params.slider_flags,
            )
        elif self.params.edit_type == FloatEditType.input:
            changed, self.value = imgui.input_float(
                self.params.label,
                self.value,
                self.params.input_step,
                self.params.input_step_fast,
                self.params.format,
                self.params.input_flags,
            )
        elif self.params.edit_type == FloatEditType.drag:
            changed, self.value = imgui.drag_float(
                self.params.label,
                self.value,
                self.params.v_speed,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                self.params.slider_flags,
            )
        elif self.params.edit_type == FloatEditType.knob:
            changed, self.value = imgui_knobs.knob(
                self.params.label,
                self.value,
                self.params.v_min,
                self.params.v_max,
                self.params.knob_speed,
                self.params.format,
                self.params.knob_variant,
                hello_imgui.em_size(self.params.knob_size_em),
                self.params.knob_steps,
            )

        return changed


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
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: False

    def edit(self) -> bool:
        assert isinstance(self.value, bool)
        changed = False
        if self.params.edit_type == BoolEditType.checkbox:
            changed, self.value = imgui.checkbox(self.params.label, self.value)
        elif self.params.edit_type == BoolEditType.radio_button:
            new_x = imgui.radio_button(self.params.label, self.value)
            if new_x != self.value:
                self.value = new_x
                changed = True
        elif self.params.edit_type == BoolEditType.toggle:
            if self.params.toggle_config is None:
                raise ValueError("toggle_config must be set for BoolEditType.toggle")
            changed, self.value = imgui_toggle.toggle(self.params.label, self.value, self.params.toggle_config)

        return changed


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
    width_em: float = 10  # if 0, then use all available width
    # Callbacks
    callback: Callable[[imgui.InputTextCallbackData], int] = None  # type: ignore
    user_data: Any | None = None
    # Specific to input_with_hint
    hint: str = ""
    # Specific to multiline
    height_em: int = 5


def _escape_double_quoted_string(s: str) -> str:
    replacements = {
        "\\": "\\\\",
        "\n": "\\n",
        "\t": "\\t",
        "\r": "\\r",
        "\b": "\\b",
        '"': '\\"',
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s


class StrWithGui(AnyDataWithGui[str]):
    params: StrWithGuiParams

    def __init__(self, params: StrWithGuiParams | None = None) -> None:
        super().__init__()
        self.params = params if params is not None else StrWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.present_str = self.present_short_str

    @staticmethod
    def present_short_str(s: str) -> str:
        if len(s) <= fiatlight.core.PRESENT_SHORT_STR_MAX_LENGTH:
            r = s
        else:
            extract = s[: fiatlight.core.PRESENT_SHORT_STR_MAX_LENGTH - 4] + "(...)"
            r = extract
        r = '"' + _escape_double_quoted_string(r) + '"'
        return r

    def edit(self) -> bool:
        assert isinstance(self.value, str)
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
        if self.params.edit_type == StrEditType.input:
            changed, self.value = imgui.input_text(
                self.params.label, self.value, self.params.input_flags, self.params.callback, self.params.user_data
            )
        elif self.params.edit_type == StrEditType.input_with_hint:
            changed, self.value = imgui.input_text_with_hint(
                self.params.label,
                self.params.hint,
                self.value,
                self.params.input_flags,
                self.params.callback,
                self.params.user_data,
            )
        elif self.params.edit_type == StrEditType.multiline:
            size = hello_imgui.em_to_vec2(self.params.width_em, self.params.height_em)
            changed, self.value = imgui.input_text_multiline(
                self.params.label,
                self.value,
                size,
                self.params.input_flags,
                self.params.callback,
                self.params.user_data,
            )

        return changed


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
]


########################################################################################################################
#                              sandbox
########################################################################################################################
