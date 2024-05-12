import fiatlight
from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, portable_file_dialogs as pfd, ImVec2, imgui_ctx
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_types import FilePath
from fiatlight.fiat_types.color_types import ColorRgb, ColorRgba
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6, fiat_osd
from fiatlight import fiat_widgets
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
    slider_and_minus_plus = 5


def available_int_edit_types() -> list[str]:
    return [e.name for e in IntEditType]


@dataclass
class IntWithGuiParams:
    edit_type: IntEditType = IntEditType.input
    # Common
    label: str = "##int"
    v_min: int = 0
    v_max: int = 100
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
    knob_flags: int = 0


class IntWithGui(AnyDataWithGui[int]):
    params: IntWithGuiParams

    def __init__(self, params: IntWithGuiParams | None = None) -> None:
        super().__init__()
        self.params = params if params is not None else IntWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: 0
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.on_heartbeat = self._on_heartbeat

    def _on_heartbeat(self) -> bool:
        self._handle_custom_attrs()
        return False

    def _check_custom_attrs(self) -> None:
        def _authorized_custom_attrs() -> list[str]:
            return ["range", "edit_type", "format", "width_em", "knob_size_em", "knob_steps"]

        has_unauthorized = any(k not in _authorized_custom_attrs() for k in self._custom_attrs)
        if has_unauthorized:
            msg = f"""
            Encountered an unauthorized custom attribute for IntWithGui!
                Authorized attributes are: {_authorized_custom_attrs()}
                Where type can be one of: {available_int_edit_types()}

            Example:
                def modulo_12(x: int) -> int:
                    return x % 12

                modulo_12.x__range = (-60, 60)
                modulo_12.x__edit_type = "knob"
                modulo_12.x__format = "%d"
                modulo_12.x__knob_size_em = 4
            """
            raise ValueError(msg)

    def _handle_custom_attrs(self) -> None:
        self._check_custom_attrs()
        if "range" in self._custom_attrs:
            range_ = self._custom_attrs["range"]
            if not isinstance(range_, tuple) or len(range_) != 2:
                raise ValueError(f"range must be a tuple of two numbers, got: {range_}")
            if not all(isinstance(x, int) for x in range_):
                raise ValueError(f"range must be a tuple of two integers, got: {range_}")
            self.params.v_min = range_[0]
            self.params.v_max = range_[1]
            self.params.edit_type = IntEditType.slider

        if "edit_type" in self._custom_attrs:
            edit_type_ = self._custom_attrs["edit_type"]
            try:
                edit_type = IntEditType[edit_type_]
                self.params.edit_type = edit_type
            except KeyError:
                raise ValueError(f"Unknown edit_type: {edit_type_}. Available types: {available_int_edit_types()}")

        if "format" in self._custom_attrs:
            self.params.format = self._custom_attrs["format"]

        if "width_em" in self._custom_attrs:
            if not isinstance(self._custom_attrs["width_em"], (int, float)):
                raise ValueError(f"width_em must be a number, got: {self._custom_attrs['width_em']}")
            self.params.width_em = self._custom_attrs["width_em"]

        if "knob_size_em" in self._custom_attrs:
            if not isinstance(self._custom_attrs["knob_size_em"], (int, float)):
                raise ValueError(f"knob_size_em must be a number, got: {self._custom_attrs['knob_size_em']}")
            self.params.knob_size_em = self._custom_attrs["knob_size_em"]

        if "knob_steps" in self._custom_attrs:
            if not isinstance(self._custom_attrs["knob_steps"], int):
                raise ValueError(f"knob_steps must be an integer, got: {self._custom_attrs['knob_steps']}")
            self.params.knob_steps = self._custom_attrs["knob_steps"]

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
                self.params.knob_flags,
                self.params.knob_steps,
            )
        if self.params.edit_type == IntEditType.slider_and_minus_plus:
            buttons_width = hello_imgui.em_size(2)
            item_width = hello_imgui.em_size(self.params.width_em) - buttons_width
            spacing = hello_imgui.em_to_vec2(0.1, 0)
            with imgui_ctx.begin_horizontal("##int", ImVec2(item_width + buttons_width, 0)):
                with imgui_ctx.push_style_var(imgui.StyleVar_.item_spacing.value, spacing):
                    imgui.set_next_item_width(item_width)
                    changed, self.value = imgui.slider_int(
                        self.params.label,
                        self.value,
                        self.params.v_min,
                        self.params.v_max,
                        self.params.format,
                        self.params.slider_flags,
                    )
                    if imgui.button("-"):
                        if self.value > self.params.v_min:
                            self.value -= 1
                            changed = True
                    if imgui.button("+"):
                        if self.value < self.params.v_max:
                            self.value += 1
                        changed = True

        return changed


########################################################################################################################
#                               Floats
########################################################################################################################
class FloatEditType(Enum):
    slider = 1
    input = 2
    drag = 3
    knob = 4
    slider_float_any_range = 5
    slider_float_any_range_positive = 6


def _available_float_edit_types() -> list[str]:
    return [e.name for e in FloatEditType]


@dataclass
class FloatWithGuiParams:
    label: str = "##float"
    v_min: float = 0.0
    v_max: float = 10.0
    format: str = "%.3f"
    width_em: float = 9
    edit_type: FloatEditType = FloatEditType.input
    # Specific to slider_float
    slider_flags: int = imgui.SliderFlags_.none.value
    # Specific to input_float
    input_step: float = 0.1
    input_step_fast: float = 1.0
    input_flags: int = imgui.InputTextFlags_.none.value
    # Specific to drag_float
    v_speed: float = 1.0
    # Specific to knob
    knob_speed: float = 1.0
    knob_variant: int = imgui_knobs.ImGuiKnobVariant_.stepped.value
    knob_size_em: float = 2.5
    knob_steps: int = 10
    knob_flags: int = 0
    # Specific to slider_float_any_range
    nb_significant_digits: int = 4
    accept_negative: bool = True


class FloatWithGui(AnyDataWithGui[float]):
    params: FloatWithGuiParams

    def __init__(self, params: FloatWithGuiParams | None = None) -> None:
        super().__init__()
        self.params = params if params is not None else FloatWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: 0.0
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.present_str = self.present_str
        self.callbacks.on_heartbeat = self._on_heartbeat

    def _on_heartbeat(self) -> bool:
        self._handle_custom_attrs()
        return False

    def _check_custom_attrs(self) -> None:
        def _authorized_custom_attrs() -> list[str]:
            return ["range", "edit_type", "format", "width_em", "knob_size_em", "knob_steps"]

        has_unauthorized = any(k not in _authorized_custom_attrs() for k in self._custom_attrs)
        if has_unauthorized:
            msg = f"""
            Encountered an unauthorized custom attribute for FloatWithGui!
                Authorized attributes are: {_authorized_custom_attrs()}
                Where type can be one of: {_available_float_edit_types()}

            Example:
                def to_fahrenheit(celsius: float) -> float:
                    return celsius * 9 / 5 + 32

                to_fahrenheit.celsius__range = (-273.15, 1000)
                to_fahrenheit.celsius__edit_type = "slider"
                to_fahrenheit.celsius__format = "%.2f °C"
                to_fahrenheit.celsius__width_em = 10

            """
            raise ValueError(msg)

    def _handle_custom_attrs(self) -> None:
        self._check_custom_attrs()
        if "range" in self._custom_attrs:
            range_ = self._custom_attrs["range"]
            if not isinstance(range_, tuple) or len(range_) != 2:
                raise ValueError(f"range must be a tuple of two numbers, got: {range_}")
            if not all(isinstance(x, (int, float)) for x in range_):
                raise ValueError(f"range must be a tuple of two numbers, got: {range_}")
            self.params.v_min = range_[0]
            self.params.v_max = range_[1]
            self.params.edit_type = FloatEditType.slider

        if "edit_type" in self._custom_attrs:
            edit_type_ = self._custom_attrs["edit_type"]
            try:
                edit_type = FloatEditType[edit_type_]
                self.params.edit_type = edit_type
                if edit_type == FloatEditType.knob:
                    self.params.format = "%.2f"
            except KeyError:
                raise ValueError(f"Unknown edit_type: {edit_type_}. Available types: {_available_float_edit_types()}")

        if "format" in self._custom_attrs:
            self.params.format = self._custom_attrs["format"]

        if "width_em" in self._custom_attrs:
            if not isinstance(self._custom_attrs["width_em"], (int, float)):
                raise ValueError(f"width_em must be a number, got: {self._custom_attrs['width_em']}")
            self.params.width_em = self._custom_attrs["width_em"]

        if "knob_size_em" in self._custom_attrs:
            if not isinstance(self._custom_attrs["knob_size_em"], (int, float)):
                raise ValueError(f"knob_size_em must be a number, got: {self._custom_attrs['knob_size_em']}")
            self.params.knob_size_em = self._custom_attrs["knob_size_em"]

        if "knob_steps" in self._custom_attrs:
            if not isinstance(self._custom_attrs["knob_steps"], int):
                raise ValueError(f"knob_steps must be an integer, got: {self._custom_attrs['knob_steps']}")
            self.params.knob_steps = self._custom_attrs["knob_steps"]

    def present_str(self, value: float) -> str:
        if self.params.nb_significant_digits >= 0:
            return f"{value:.{self.params.nb_significant_digits}g}"
        else:
            return str(value)

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
                self.params.knob_flags,
                self.params.knob_steps,
            )
        elif (
            self.params.edit_type == FloatEditType.slider_float_any_range
            or self.params.edit_type == FloatEditType.slider_float_any_range_positive
        ):
            from fiatlight.fiat_widgets.float_widgets import slider_float_any_range

            accept_negative = self.params.accept_negative
            if self.params.edit_type == FloatEditType.slider_float_any_range_positive:
                accept_negative = False

            changed, self.value = slider_float_any_range(
                self.params.label,
                self.value,
                accept_negative,
                self.params.nb_significant_digits,
            )

        return changed


def make_positive_float_with_gui() -> AnyDataWithGui[float]:
    params = FloatWithGuiParams(edit_type=FloatEditType.slider_float_any_range_positive, nb_significant_digits=4)
    r = FloatWithGui(params)
    return r


########################################################################################################################
#                               Bool
########################################################################################################################
class BoolEditType(Enum):
    checkbox = 1
    toggle = 3


def _available_bool_edit_types() -> list[str]:
    return [e.name for e in BoolEditType]


@dataclass
class BoolWithGuiParams:
    default_edit_value = False
    label: str = "##bool"
    edit_type: BoolEditType = BoolEditType.checkbox


class BoolWithGui(AnyDataWithGui[bool]):
    params: BoolWithGuiParams

    def __init__(self, params: BoolWithGuiParams | None = None):
        super().__init__()
        self.params = params if params is not None else BoolWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: False
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.on_heartbeat = self._on_heartbeat

    def _on_heartbeat(self) -> bool:
        self._handle_custom_attrs()
        return False

    def _check_custom_attrs(self) -> None:
        def _authorized_custom_attrs() -> list[str]:
            return ["edit_type"]

        has_unauthorized = any(k not in _authorized_custom_attrs() for k in self._custom_attrs)
        if has_unauthorized:
            msg = f"""
            Encountered an unauthorized custom attribute for BoolWithGui!
                Authorized attributes are: {_authorized_custom_attrs()}
                Where type can be one of: {_available_bool_edit_types()}

            Example:
                def is_even(x: int) -> bool:
                    return x % 2 == 0

                is_even.x__edit_type = "radio_button"
            """
            raise ValueError(msg)

    def _handle_custom_attrs(self) -> None:
        self._check_custom_attrs()
        if "edit_type" in self._custom_attrs:
            edit_type_ = self._custom_attrs["edit_type"]
            try:
                edit_type = BoolEditType[edit_type_]
                self.params.edit_type = edit_type
            except KeyError:
                raise ValueError(f"Unknown edit_type: {edit_type_}. Available types: {_available_bool_edit_types()}")

    def edit(self) -> bool:
        assert isinstance(self.value, bool)
        changed = False
        if self.params.edit_type == BoolEditType.checkbox:
            changed, self.value = imgui.checkbox(self.params.label, self.value)
        elif self.params.edit_type == BoolEditType.toggle:
            # if self.params.toggle_config is None:
            #     raise ValueError("toggle_config must be set for BoolEditType.toggle")
            changed, self.value = imgui_toggle.toggle(
                self.params.label, self.value, imgui_toggle.ToggleFlags_.animated.value
            )

        return changed


########################################################################################################################
#                               Str
########################################################################################################################
class StrEditType(Enum):
    input = 1
    versatile = 2
    multiline = 3  # multiline text input does *not* work inside a Node (only in a popup)


@dataclass
class StrWithGuiParams:
    default_edit_value = ""
    label: str = "##str"
    edit_type: StrEditType = StrEditType.versatile
    input_flags: int = imgui.InputTextFlags_.none.value
    # Callbacks
    callback: Callable[[imgui.InputTextCallbackData], int] = None  # type: ignore
    user_data: Any | None = None
    # Will display this hint if the string is empty
    hint: str = ""
    # Only used if edit_type is input (not multiline)
    width_em_one_line: float = 10
    # status
    versatile_edit_as_multiline: bool | None = None


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
        self.callbacks.present_custom_popup_required = False
        self.callbacks.present_custom_popup_possible = True
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.on_heartbeat = self.on_heartbeat

    @staticmethod
    def present_str(s: str) -> str:
        return s

    def on_heartbeat(self) -> bool:
        if self.params.edit_type == StrEditType.versatile:
            # Compute if the string should be edited as multiline
            # (if it is long or contains newlines)
            if self.params.versatile_edit_as_multiline is None:
                use_multiline = False
                value = self.value
                if isinstance(value, str):
                    if len(value) > 60:
                        use_multiline = True
                    if "\n" in value:
                        use_multiline = True
                self.params.versatile_edit_as_multiline = use_multiline

            self.callbacks.edit_popup_required = self.params.versatile_edit_as_multiline
        if self.params.edit_type == StrEditType.multiline:
            self.callbacks.edit_popup_required = True
        return False

    def present_custom(self) -> None:
        text_value = self.get_actual_value()
        if fiatlight.is_rendering_in_window():
            text_edit_size = ImVec2(
                imgui.get_window_width() - hello_imgui.em_size(1), imgui.get_window_height() - hello_imgui.em_size(5)
            )
            imgui.input_text_multiline("##str", text_value, text_edit_size, imgui.InputTextFlags_.read_only.value)
        else:
            fiat_widgets.text_maybe_truncated(
                text_value,
                max_width_chars=50,
                max_lines=5,
            )

    def edit(self) -> bool:
        assert isinstance(self.value, str)
        changed = False
        present_multiline = False
        is_versatile = self.params.edit_type == StrEditType.versatile
        if is_versatile:
            assert self.params.versatile_edit_as_multiline is not None
            present_multiline = self.params.versatile_edit_as_multiline
        if self.params.edit_type == StrEditType.multiline:
            present_multiline = True

        if not present_multiline:
            imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em_one_line))
            has_hint = len(self.params.hint) > 0
            if has_hint:
                changed, self.value = imgui.input_text_with_hint(
                    self.params.label,
                    self.params.hint,
                    self.value,
                    self.params.input_flags,
                    self.params.callback,
                    self.params.user_data,
                )
            else:
                changed, self.value = imgui.input_text(
                    self.params.label, self.value, self.params.input_flags, self.params.callback, self.params.user_data
                )

            if is_versatile:
                imgui.same_line()
                with fontawesome_6_ctx():
                    if imgui.button(icons_fontawesome_6.ICON_FA_BARS):
                        self.params.versatile_edit_as_multiline = True
                    fiat_osd.set_widget_tooltip("Edit in popup (multiline)")
        else:  # present_multiline
            assert isinstance(self.value, str)
            size = ImVec2(0, 0)
            size.x = imgui.get_window_width() - hello_imgui.em_size(1)
            size.y = imgui.get_window_height() - hello_imgui.em_size(5)

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
#                               Specialized strings
########################################################################################################################
class StrMultilineWithGui(StrWithGui):
    def __init__(self, params: StrWithGuiParams | None = None) -> None:
        super().__init__(params)
        self.callbacks.edit_popup_required = True
        self.params.edit_type = StrEditType.multiline


class PromptWithGui(StrMultilineWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.params.hint = "Enter a prompt here"


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
        try:
            as_path = Path(value)
            r = str(as_path.name) + "\n"
            r += str(as_path.absolute())
            return r
        except TypeError:
            return "???"


class ImagePathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]


class TextPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.txt"]


class AudioPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.wav", "*.mp3", "*.ogg", "*.flac"]


class VideoPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.mp4", "*.avi", "*.mkv"]


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


########################################################################################################################
#                               Register all types
########################################################################################################################
def __register_file_paths_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_types import FilePath, TextPath, ImagePath, AudioPath, VideoPath

    register_type(FilePath, FilePathWithGui)
    register_type(TextPath, TextPathWithGui)
    register_type(ImagePath, ImagePathWithGui)
    register_type(AudioPath, AudioPathWithGui)
    register_type(VideoPath, VideoPathWithGui)


def __register_python_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(int, IntWithGui)
    register_type(float, FloatWithGui)
    register_type(str, StrWithGui)
    register_type(bool, BoolWithGui)


def __register_color_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(ColorRgb, ColorRgbWithGui)
    register_type(ColorRgba, ColorRgbaWithGui)


def __register_custom_float_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_types import PositiveFloat

    register_type(PositiveFloat, make_positive_float_with_gui)


def _register_custom_str_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_types.str_types import Prompt, StrMultiline

    register_type(Prompt, PromptWithGui)
    register_type(StrMultiline, StrMultilineWithGui)


def _register_all_primitive_types() -> None:
    __register_file_paths_types()
    __register_python_types()
    __register_color_types()
    __register_custom_float_types()
    _register_custom_str_types()
