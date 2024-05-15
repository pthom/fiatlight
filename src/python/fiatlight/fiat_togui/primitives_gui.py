import os.path

from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, portable_file_dialogs as pfd, ImVec2, imgui_ctx
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_types import FilePath, FilePath_Save
from fiatlight.fiat_types.color_types import ColorRgb, ColorRgba
from typing import Callable, TypeAlias
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
    slider_logarithmic: bool = False
    slider_no_input: bool = False
    # Specific to input_int
    input_flags: int = imgui.InputTextFlags_.none.value
    input_step: int = 1
    input_step_fast: int = 100
    # Specific to drag
    v_speed: float = 1.0
    # Specific to knob
    knob_speed: float = 0.0
    knob_variant: int = ImGuiKnobVariant_.stepped.value
    knob_size_em: float = 2.5
    knob_steps: int = 10
    knob_no_input: bool = True


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
            return [
                "range",
                "edit_type",
                "format",
                "width_em",
                "knob_size_em",
                "knob_steps",
                "knob_no_input",
                "slider_no_input",
                "slider_logarithmic",
            ]

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

        if "knob_no_input" in self._custom_attrs:
            if not isinstance(self._custom_attrs["knob_no_input"], bool):
                raise ValueError(f"knob_no_input must be a boolean, got: {self._custom_attrs['knob_no_input']}")
            self.params.knob_no_input = self._custom_attrs["knob_no_input"]

        if "slider_no_input" in self._custom_attrs:
            if not isinstance(self._custom_attrs["slider_no_input"], bool):
                raise ValueError(f"slider_no_input must be a boolean, got: {self._custom_attrs['slider_no_input']}")
            self.params.slider_no_input = self._custom_attrs["slider_no_input"]

        if "slider_logarithmic" in self._custom_attrs:
            if not isinstance(self._custom_attrs["slider_logarithmic"], bool):
                raise ValueError(
                    f"slider_logarithmic must be a boolean, got: {self._custom_attrs['slider_logarithmic']}"
                )
            self.params.slider_logarithmic = self._custom_attrs["slider_logarithmic"]

    def edit(self, value: int) -> tuple[bool, int]:
        if not isinstance(value, int):
            raise ValueError(f"IntWithGui expects an int, got: {type(value)}")
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
        if self.params.edit_type == IntEditType.slider:
            slider_flags = 0
            if self.params.slider_logarithmic:
                slider_flags = imgui.SliderFlags_.logarithmic.value
            if self.params.slider_no_input:
                slider_flags |= imgui.SliderFlags_.no_input.value
            changed, value = imgui.slider_int(
                self.params.label,
                value,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                slider_flags,
            )
        elif self.params.edit_type == IntEditType.input:
            changed, value = imgui.input_int(
                self.params.label,
                value,
                self.params.input_step,
                self.params.input_step_fast,
                self.params.input_flags,
            )
        elif self.params.edit_type == IntEditType.drag:
            slider_flags = 0
            if self.params.slider_logarithmic:
                slider_flags = imgui.SliderFlags_.logarithmic.value
            if self.params.slider_no_input:
                slider_flags |= imgui.SliderFlags_.no_input.value
            changed, value = imgui.drag_int(
                self.params.label,
                value,
                self.params.v_speed,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                slider_flags,
            )
        elif self.params.edit_type == IntEditType.knob:
            knob_flags = 0
            if self.params.knob_no_input:
                knob_flags = imgui_knobs.ImGuiKnobFlags_.no_input.value
            changed, value = imgui_knobs.knob_int(
                self.params.label,
                value,
                self.params.v_min,
                self.params.v_max,
                self.params.knob_speed,
                self.params.format,
                self.params.knob_variant,
                hello_imgui.em_size(self.params.knob_size_em),
                knob_flags,
                self.params.knob_steps,
            )
        if self.params.edit_type == IntEditType.slider_and_minus_plus:
            buttons_width = hello_imgui.em_size(2)
            item_width = hello_imgui.em_size(self.params.width_em) - buttons_width
            spacing = hello_imgui.em_to_vec2(0.1, 0)
            with imgui_ctx.begin_horizontal("##int", ImVec2(item_width + buttons_width, 0)):
                with imgui_ctx.push_style_var(imgui.StyleVar_.item_spacing.value, spacing):
                    slider_flags = 0
                    if self.params.slider_logarithmic:
                        slider_flags = imgui.SliderFlags_.logarithmic.value
                    imgui.set_next_item_width(item_width)
                    changed, value = imgui.slider_int(
                        self.params.label,
                        value,
                        self.params.v_min,
                        self.params.v_max,
                        self.params.format,
                        slider_flags,
                    )
                    if imgui.button("-"):
                        if value > self.params.v_min:
                            value -= 1
                            changed = True
                    if imgui.button("+"):
                        if value < self.params.v_max:
                            value += 1
                        changed = True

        return changed, value


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
    knob_no_input: bool = False  # Disable text input on knobs and sliders
    # Specific to slider
    slider_logarithmic: bool = False
    slider_no_input: bool = False
    # Specific to input_float
    input_step: float = 0.1
    input_step_fast: float = 1.0
    input_flags: int = imgui.InputTextFlags_.none.value
    # Specific to drag_float
    v_speed: float = 1.0
    # Specific to knob
    knob_speed: float = 0.1
    knob_variant: int = imgui_knobs.ImGuiKnobVariant_.stepped.value
    knob_size_em: float = 2.5
    knob_steps: int = 10
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
            return [
                "range",
                "edit_type",
                "format",
                "width_em",
                "knob_size_em",
                "knob_steps",
                "knob_no_input",
                "slider_no_input",
                "slider_logarithmic",
            ]

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

        if "knob_no_input" in self._custom_attrs:
            if not isinstance(self._custom_attrs["knob_no_input"], bool):
                raise ValueError(f"knob_no_input must be a boolean, got: {self._custom_attrs['knob_no_input']}")
            self.params.knob_no_input = self._custom_attrs["knob_no_input"]

        if "slider_no_input" in self._custom_attrs:
            if not isinstance(self._custom_attrs["slider_no_input"], bool):
                raise ValueError(f"slider_no_input must be a boolean, got: {self._custom_attrs['slider_no_input']}")
            self.params.slider_no_input = self._custom_attrs["slider_no_input"]

        if "slider_logarithmic" in self._custom_attrs:
            if not isinstance(self._custom_attrs["slider_logarithmic"], bool):
                raise ValueError(
                    f"slider_logarithmic must be a boolean, got: {self._custom_attrs['slider_logarithmic']}"
                )
            self.params.slider_logarithmic = self._custom_attrs["slider_logarithmic"]

    def present_str(self, value: float) -> str:
        if self.params.nb_significant_digits >= 0:
            return f"{value:.{self.params.nb_significant_digits}g}"
        else:
            return str(value)

    def edit(self, value: float) -> tuple[bool, float]:
        if not isinstance(value, float) and not isinstance(value, int):
            raise ValueError(f"FloatWithGui expects a float, got: {type(value)}")
        changed = False
        imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
        if self.params.edit_type == FloatEditType.slider:
            slider_flags = 0
            if self.params.slider_logarithmic:
                slider_flags = imgui.SliderFlags_.logarithmic.value
            if self.params.slider_no_input:
                slider_flags |= imgui.SliderFlags_.no_input.value
            changed, value = imgui.slider_float(
                self.params.label,
                value,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                slider_flags,
            )
        elif self.params.edit_type == FloatEditType.input:
            changed, value = imgui.input_float(
                self.params.label,
                value,
                self.params.input_step,
                self.params.input_step_fast,
                self.params.format,
                self.params.input_flags,
            )
        elif self.params.edit_type == FloatEditType.drag:
            slider_flags = 0
            if self.params.slider_logarithmic:
                slider_flags = imgui.SliderFlags_.logarithmic.value
            if self.params.slider_no_input:
                slider_flags |= imgui.SliderFlags_.no_input.value
            changed, value = imgui.drag_float(
                self.params.label,
                value,
                self.params.v_speed,
                self.params.v_min,
                self.params.v_max,
                self.params.format,
                slider_flags,
            )
        elif self.params.edit_type == FloatEditType.knob:
            knob_flags = 0
            if self.params.knob_no_input:
                knob_flags = imgui_knobs.ImGuiKnobFlags_.no_input.value
            changed, value = imgui_knobs.knob(
                self.params.label,
                value,
                self.params.v_min,
                self.params.v_max,
                self.params.knob_speed,
                self.params.format,
                self.params.knob_variant,
                hello_imgui.em_size(self.params.knob_size_em),
                knob_flags,
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

            changed, value = slider_float_any_range(
                self.params.label,
                value,
                accept_negative,
                self.params.nb_significant_digits,
            )

        return changed, value


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

    def edit(self, value: bool) -> tuple[bool, bool]:
        if not isinstance(value, bool):
            raise ValueError(f"BoolWithGui expects a bool, got: {type(value)}")
        changed = False
        if self.params.edit_type == BoolEditType.checkbox:
            changed, value = imgui.checkbox(self.params.label, value)
        elif self.params.edit_type == BoolEditType.toggle:
            # if self.params.toggle_config is None:
            #     raise ValueError("toggle_config must be set for BoolEditType.toggle")
            changed, value = imgui_toggle.toggle(self.params.label, value, imgui_toggle.ToggleFlags_.animated.value)

        return changed, value


########################################################################################################################
#                               Str: see str_with_resizable_gui.py
########################################################################################################################


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

    def edit(self, value: FilePath) -> tuple[bool, FilePath]:
        from fiatlight.fiat_widgets import fiat_osd

        changed = False
        if imgui.button("Select file"):
            self._open_file_dialog = pfd.open_file("Select file", self.default_path, self.filters)
        if self._open_file_dialog is not None and self._open_file_dialog.ready():
            if len(self._open_file_dialog.result()) == 1:
                selected_file = self._open_file_dialog.result()[0]
                value = FilePath(selected_file)
                changed = True
            self._open_file_dialog = None
        if len(value) > 0:
            basename = os.path.basename(value)
            imgui.same_line()
            imgui.text(basename)
            fiat_osd.set_widget_tooltip(value)
        return changed, value

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


class FilePathSaveWithGui(AnyDataWithGui[FilePath_Save]):
    filters: list[str]
    default_path: str = ""

    _save_file_dialog: pfd.save_file | None = None

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: FilePath_Save("")
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_str = lambda x: str(x)
        self.callbacks.clipboard_copy_possible = True
        self.filters = []

    def edit(self, value: FilePath_Save) -> tuple[bool, FilePath_Save]:
        from fiatlight.fiat_widgets import fiat_osd

        changed = False
        if imgui.button("Select save file"):
            self._save_file_dialog = pfd.save_file("Select file", self.default_path, self.filters)
        if self._save_file_dialog is not None and self._save_file_dialog.ready():
            selected_file = self._save_file_dialog.result()
            value = FilePath_Save(selected_file)
            changed = True
            self._open_file_dialog = None

        if len(value) > 0:
            basename = os.path.basename(value)
            imgui.same_line()
            imgui.text(basename)
            fiat_osd.set_widget_tooltip(value)
        return changed, value

    @staticmethod
    def present_str(value: FilePath_Save) -> str:
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


class ImagePathSaveWithGui(FilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]


class TextPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.txt, *.*"]


class TextPathSaveWithGui(FilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.txt, *.*"]


class AudioPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.aiff", "*.m4a"]


class AudioPathSaveWithGui(FilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.aiff", "*.m4a"]


class VideoPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.mp4", "*.avi", "*.mkv"]


class VideoPathSaveWithGui(FilePathSaveWithGui):
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

    @staticmethod
    def edit(value: ColorRgb) -> tuple[bool, ColorRgb]:
        if not isinstance(value, tuple):
            raise ValueError(f"ColorRgbWithGui expects a tuple, got: {type(value)}")
        if len(value) != 3:
            raise ValueError(f"ColorRgbWithGui expects a tuple of 3 ints, got: {value}")
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
            value = ColorRgb(
                (
                    int(value_as_floats[0] * 255),
                    int(value_as_floats[1] * 255),
                    int(value_as_floats[2] * 255),
                )
            )
            return True, value
        else:
            return False, value

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

    @staticmethod
    def edit(value: ColorRgba) -> tuple[bool, ColorRgba]:
        if not isinstance(value, tuple):
            raise ValueError(f"ColorRgbaWithGui expects a tuple, got: {type(value)}")
        if len(value) != 4:
            raise ValueError(f"ColorRgbaWithGui expects a tuple of 4 ints, got: {value}")
        value_as_floats = [value[0] / 255.0, value[1] / 255.0, value[2] / 255.0, value[3] / 255.0]
        changed, value_as_floats = imgui.color_edit4("##color", value_as_floats)
        if changed:
            value = ColorRgba(
                (
                    int(value_as_floats[0] * 255),
                    int(value_as_floats[1] * 255),
                    int(value_as_floats[2] * 255),
                    int(value_as_floats[3] * 255),
                )
            )
            return True, value
        else:
            return False, value

    @staticmethod
    def present_str(value: ColorRgba) -> str:
        return f"R: {value[0]}, G: {value[1]}, B: {value[2]}, A: {value[3]}"


########################################################################################################################
#                               Register all types
########################################################################################################################
def __register_file_paths_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_types import (
        FilePath,
        TextPath,
        ImagePath,
        AudioPath,
        VideoPath,
        FilePath_Save,
        TextPath_Save,
        ImagePath_Save,
        AudioPath_Save,
        VideoPath_Save,
    )

    register_type(FilePath, FilePathWithGui)
    register_type(TextPath, TextPathWithGui)
    register_type(ImagePath, ImagePathWithGui)
    register_type(AudioPath, AudioPathWithGui)
    register_type(VideoPath, VideoPathWithGui)
    register_type(FilePath_Save, FilePathSaveWithGui)
    register_type(TextPath_Save, TextPathSaveWithGui)
    register_type(ImagePath_Save, ImagePathSaveWithGui)
    register_type(AudioPath_Save, AudioPathSaveWithGui)
    register_type(VideoPath_Save, VideoPathSaveWithGui)


def __register_python_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from .str_with_resizable_gui import StrWithResizableGui

    register_type(int, IntWithGui)
    register_type(float, FloatWithGui)
    register_type(str, StrWithResizableGui)
    register_type(bool, BoolWithGui)


def __register_color_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(ColorRgb, ColorRgbWithGui)
    register_type(ColorRgba, ColorRgbaWithGui)


def __register_custom_float_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_types import PositiveFloat

    register_type(PositiveFloat, make_positive_float_with_gui)


def _register_all_primitive_types() -> None:
    __register_file_paths_types()
    __register_python_types()
    __register_color_types()
    __register_custom_float_types()
