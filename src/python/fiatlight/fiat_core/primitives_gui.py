from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, portable_file_dialogs as pfd, ImVec2
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_types import FilePath
from fiatlight.fiat_types.color_types import ColorRgb, ColorRgba
from typing import Any, Callable, TypeAlias
from dataclasses import dataclass
from enum import Enum


GuiFunction = Callable[[], None]


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
    width_em: float = 9
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
        self.callbacks.clipboard_copy_possible = True

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
    width_em: float = 9
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
        self.callbacks.clipboard_copy_possible = True

    def edit(self) -> bool:
        assert isinstance(self.value, float) or isinstance(self.value, int)
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
        self.callbacks.clipboard_copy_possible = True

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


class StrWithGui(AnyDataWithGui[str]):
    params: StrWithGuiParams

    def __init__(self, params: StrWithGuiParams | None = None) -> None:
        super().__init__()
        self.params = params if params is not None else StrWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.present_str = self.present_str
        if self.params.edit_type == StrEditType.multiline:
            self.callbacks.edit_popup_required = True

        self.callbacks.present_custom = self.present_custom
        self.callbacks.present_custom_popup_required = True
        self.callbacks.clipboard_copy_possible = True

    @staticmethod
    def present_str(s: str) -> str:
        return s

    def present_custom(self) -> None:
        text_value = self.get_actual_value()
        text_edit_size = ImVec2(
            imgui.get_window_width() - hello_imgui.em_size(1), imgui.get_window_height() - hello_imgui.em_size(5)
        )
        imgui.input_text_multiline("##str", text_value, text_edit_size, imgui.InputTextFlags_.read_only.value)

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
            self.callbacks.edit_popup_required = True
            assert isinstance(self.value, str)
            size = ImVec2(0, 0)
            size.x = imgui.get_window_width()
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
#                               File selector
########################################################################################################################
class FilePathWithGui(AnyDataWithGui[FilePath]):
    filters: list[str]
    default_path: str = ""

    _open_file_dialog: pfd.open_file | None = None

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: FilePath("")
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_str = lambda x: str(x)
        self.callbacks.clipboard_copy_possible = True
        self.filters = []

    def edit(self) -> bool:
        changed = False
        if imgui.button("Select file"):
            self._open_file_dialog = pfd.open_file("Select file", self.default_path, self.filters)
        if self._open_file_dialog is not None and self._open_file_dialog.ready():
            if len(self._open_file_dialog.result()) == 1:
                selected_file = self._open_file_dialog.result()[0]
                self.value = FilePath(selected_file)
                changed = True
            self._open_file_dialog = None
        return changed

    @staticmethod
    def present_str(value: FilePath) -> str:
        from pathlib import Path

        # Returns two lines: the file name and the full path
        # (which will be presented as a tooltip)
        as_path = Path(value)
        r = str(as_path.name) + "\n"
        r += str(as_path.absolute())
        return r


class ImagePathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]


class TextPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.txt"]


########################################################################################################################
#                               ColorRbg and ColorRgba
########################################################################################################################
class ColorRgbWithGui(AnyDataWithGui[ColorRgb]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: ColorRgb((0, 0, 0))
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_possible = True

    def edit(self) -> bool:
        assert isinstance(self.value, tuple)
        assert len(self.value) == 3
        value = self.value
        value_as_floats = [value[0] / 255.0, value[1] / 255.0, value[2] / 255.0]

        imgui.text("Edit")

        picker_flags_std = imgui.ColorEditFlags_.no_side_preview.value
        picker_flags_wheel = imgui.ColorEditFlags_.picker_hue_wheel.value | imgui.ColorEditFlags_.no_inputs.value

        imgui.set_next_item_width(hello_imgui.em_size(8))
        changed1, value_as_floats = imgui.color_picker3("##color", value_as_floats, picker_flags_std)
        imgui.same_line()
        imgui.set_next_item_width(hello_imgui.em_size(8))
        changed2, value_as_floats = imgui.color_picker3("##color", value_as_floats, picker_flags_wheel)
        if changed1 or changed2:
            self.value = ColorRgb(
                (
                    int(value_as_floats[0] * 255),
                    int(value_as_floats[1] * 255),
                    int(value_as_floats[2] * 255),
                )
            )
            return True
        else:
            return False

    @staticmethod
    def present_str(value: ColorRgb) -> str:
        return f"R: {value[0]}, G: {value[1]}, B: {value[2]}"


class ColorRgbaWithGui(AnyDataWithGui[ColorRgba]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: ColorRgba((0, 0, 0, 255))
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_possible = True

    def edit(self) -> bool:
        assert isinstance(self.value, tuple)
        assert len(self.value) == 4
        value = self.value
        value_as_floats = [value[0] / 255.0, value[1] / 255.0, value[2] / 255.0, value[3] / 255.0]
        changed, value_as_floats = imgui.color_edit4("##color", value_as_floats)
        if changed:
            self.value = ColorRgba(
                (
                    int(value_as_floats[0] * 255),
                    int(value_as_floats[1] * 255),
                    int(value_as_floats[2] * 255),
                    int(value_as_floats[3] * 255),
                )
            )
            return True
        else:
            return False

    @staticmethod
    def present_str(value: ColorRgba) -> str:
        return f"R: {value[0]}, G: {value[1]}, B: {value[2]}, A: {value[3]}"
