from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, ImVec2, imgui_ctx, ImVec4
from fiatlight.fiat_core import AnyDataWithGui, PossibleFiatAttributes
from fiatlight.fiat_types.color_types import ColorRgb, ColorRgba, ColorRgbFloat, ColorRgbaFloat
from fiatlight.fiat_types import FiatAttributes
from typing import Callable, TypeAlias
from dataclasses import dataclass
import math
from enum import Enum


GuiFunction = Callable[[], None]


########################################################################################################################
#                               Ints
########################################################################################################################
ImGuiKnobVariant_: TypeAlias = imgui_knobs.ImGuiKnobVariant_
ToggleConfig: TypeAlias = imgui_toggle.ToggleConfig


class _PossibleIntAttributes(PossibleFiatAttributes):
    def __init__(self) -> None:
        super().__init__("IntWithGui")
        self.add_explained_attribute(
            "range", tuple, "Range of the integer", tuple_types=(int, int), default_value=(0, 10)
        )
        self.add_explained_attribute(
            "edit_type",
            str,
            "Type of the edit widget. Possible values: slider, input, drag, knob, slider_and_minus_plus",
            default_value="input",
        )
        self.add_explained_attribute("format", str, "Format string for the value", default_value="%d")
        self.add_explained_attribute("width_em", float, "Width of the widget in em", default_value=9.0)
        self.add_explained_attribute("knob_size_em", float, "Size of the knob in em", default_value=2.5)
        self.add_explained_attribute("knob_steps", int, "Number of steps in the knob", default_value=10)
        self.add_explained_attribute(
            "knob_no_input", bool, "Disable text input on knobs and sliders", default_value=True
        )
        self.add_explained_attribute("slider_no_input", bool, "Disable text input on sliders", default_value=False)
        self.add_explained_attribute(
            "slider_logarithmic", bool, "Use a logarithmic scale for sliders", default_value=False
        )


_POSSIBLE_INT_ATTRIBUTES = _PossibleIntAttributes()


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
    knob_no_input: bool = False


class IntWithGui(AnyDataWithGui[int]):
    """A highly customizable int widget."""

    params: IntWithGuiParams

    def __init__(self, params: IntWithGuiParams | None = None) -> None:
        super().__init__(int)
        self.params = params if params is not None else IntWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: 0
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.on_fiat_attributes_changed = self._handle_fiat_attrs
        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _POSSIBLE_INT_ATTRIBUTES

    def _handle_fiat_attrs(self, fiat_attrs: FiatAttributes) -> None:
        if "range" in self.fiat_attributes:
            range_ = self.fiat_attributes["range"]
            self.params.v_min = range_[0]
            self.params.v_max = range_[1]
            self.params.edit_type = IntEditType.slider

        if "edit_type" in self.fiat_attributes:
            edit_type_ = self.fiat_attributes["edit_type"]
            try:
                edit_type = IntEditType[edit_type_]
                self.params.edit_type = edit_type
            except KeyError:
                raise ValueError(f"Unknown edit_type: {edit_type_}. Available types: {available_int_edit_types()}")

        if "format" in self.fiat_attributes:
            self.params.format = self.fiat_attributes["format"]

        if "width_em" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["width_em"], (int, float)):
                raise ValueError(f"width_em must be a number, got: {self.fiat_attributes['width_em']}")
            self.params.width_em = self.fiat_attributes["width_em"]

        if "knob_size_em" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["knob_size_em"], (int, float)):
                raise ValueError(f"knob_size_em must be a number, got: {self.fiat_attributes['knob_size_em']}")
            self.params.knob_size_em = self.fiat_attributes["knob_size_em"]

        if "knob_steps" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["knob_steps"], int):
                raise ValueError(f"knob_steps must be an integer, got: {self.fiat_attributes['knob_steps']}")
            self.params.knob_steps = self.fiat_attributes["knob_steps"]

        if "knob_no_input" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["knob_no_input"], bool):
                raise ValueError(f"knob_no_input must be a boolean, got: {self.fiat_attributes['knob_no_input']}")
            self.params.knob_no_input = self.fiat_attributes["knob_no_input"]

        if "slider_no_input" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["slider_no_input"], bool):
                raise ValueError(f"slider_no_input must be a boolean, got: {self.fiat_attributes['slider_no_input']}")
            self.params.slider_no_input = self.fiat_attributes["slider_no_input"]

        if "slider_logarithmic" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["slider_logarithmic"], bool):
                raise ValueError(
                    f"slider_logarithmic must be a boolean, got: {self.fiat_attributes['slider_logarithmic']}"
                )
            self.params.slider_logarithmic = self.fiat_attributes["slider_logarithmic"]

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


class PossibleFloatAttributes(PossibleFiatAttributes):
    def __init__(self) -> None:
        super().__init__("FloatWithGui")
        self.add_explained_attribute(
            "range", tuple, "Range of the float", tuple_types=(float, float), default_value=(0.0, 10.0)
        )
        self.add_explained_attribute(
            "edit_type",
            str,
            "Type of the edit widget. Possible values: slider, input, drag, knob, slider_float_any_range, slider_float_any_range_positive",
            default_value="input",
        )
        self.add_explained_attribute("format", str, "Format string for the value", default_value="%.3f")
        self.add_explained_attribute("width_em", float, "Width of the widget in em", default_value=9.0)
        self.add_explained_attribute("knob_size_em", float, "Size of the knob in em", default_value=2.5)
        self.add_explained_attribute("knob_steps", int, "Number of steps in the knob", default_value=10)
        self.add_explained_attribute(
            "knob_no_input", bool, "Disable text input on knobs and sliders", default_value=False
        )
        self.add_explained_attribute("slider_no_input", bool, "Disable text input on sliders", default_value=False)
        self.add_explained_attribute(
            "slider_logarithmic", bool, "Use a logarithmic scale for sliders", default_value=False
        )


_POSSIBLE_FLOAT_ATTRIBUTES = PossibleFloatAttributes()


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
    """A highly customizable float widget."""

    params: FloatWithGuiParams

    def __init__(self, params: FloatWithGuiParams | None = None) -> None:
        super().__init__(float)
        self.params = params if params is not None else FloatWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: 0.0
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.present_str = self.present_str
        self.callbacks.on_fiat_attributes_changed = self._handle_fiat_attrs
        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _POSSIBLE_FLOAT_ATTRIBUTES

    def _handle_fiat_attrs(self, fiat_attrs: FiatAttributes) -> None:
        if "range" in self.fiat_attributes:
            range_ = self.fiat_attributes["range"]
            if not isinstance(range_, tuple) or len(range_) != 2:
                raise ValueError(f"range must be a tuple of two numbers, got: {range_}")
            if not all(isinstance(x, (int, float)) for x in range_):
                raise ValueError(f"range must be a tuple of two numbers, got: {range_}")
            self.params.v_min = range_[0]
            self.params.v_max = range_[1]
            self.params.edit_type = FloatEditType.slider

        if "edit_type" in self.fiat_attributes:
            edit_type_ = self.fiat_attributes["edit_type"]
            try:
                edit_type = FloatEditType[edit_type_]
                self.params.edit_type = edit_type
                if edit_type == FloatEditType.knob:
                    self.params.format = "%.2f"
            except KeyError:
                raise ValueError(f"Unknown edit_type: {edit_type_}. Available types: {_available_float_edit_types()}")

        if "format" in self.fiat_attributes:
            self.params.format = self.fiat_attributes["format"]

        if "width_em" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["width_em"], (int, float)):
                raise ValueError(f"width_em must be a number, got: {self.fiat_attributes['width_em']}")
            self.params.width_em = self.fiat_attributes["width_em"]

        if "knob_size_em" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["knob_size_em"], (int, float)):
                raise ValueError(f"knob_size_em must be a number, got: {self.fiat_attributes['knob_size_em']}")
            self.params.knob_size_em = self.fiat_attributes["knob_size_em"]

        if "knob_steps" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["knob_steps"], int):
                raise ValueError(f"knob_steps must be an integer, got: {self.fiat_attributes['knob_steps']}")
            self.params.knob_steps = self.fiat_attributes["knob_steps"]

        if "knob_no_input" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["knob_no_input"], bool):
                raise ValueError(f"knob_no_input must be a boolean, got: {self.fiat_attributes['knob_no_input']}")
            self.params.knob_no_input = self.fiat_attributes["knob_no_input"]

        if "slider_no_input" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["slider_no_input"], bool):
                raise ValueError(f"slider_no_input must be a boolean, got: {self.fiat_attributes['slider_no_input']}")
            self.params.slider_no_input = self.fiat_attributes["slider_no_input"]

        if "slider_logarithmic" in self.fiat_attributes:
            if not isinstance(self.fiat_attributes["slider_logarithmic"], bool):
                raise ValueError(
                    f"slider_logarithmic must be a boolean, got: {self.fiat_attributes['slider_logarithmic']}"
                )
            self.params.slider_logarithmic = self.fiat_attributes["slider_logarithmic"]

        def auto_handle_format_and_logarithmic() -> None:
            # When both v_min and v_max are positive and not zero,
            # we can infer the format and slider_logarithmic:
            # - format: we need to display the number with enough precision
            # - slider_logarithmic: if the difference in log10 value is large a logarithmic scale is more appropriate
            both_positive_not_zero = self.params.v_min > 0 and self.params.v_max > 0
            if both_positive_not_zero:
                v_min = self.params.v_min
                if "format" not in self.fiat_attributes:
                    # Update format if the range requires more precision
                    epsilon = 0.01  # minimum reachable by default format "%.3f" is 0.001
                    if self.params.v_min < epsilon:
                        nb_digits_after_dot = int(-math.log10(v_min)) + 1 + 3
                        self.params.format = f"%.{nb_digits_after_dot}f"
                if "slider_logarithmic" not in self.fiat_attributes:
                    # Update slider_logarithmic if difference in log10 value is large and both values are same sign
                    log10_max_diff = 3
                    vmax_min_log_diff = math.log10(self.params.v_max) - math.log10(self.params.v_min)
                    if vmax_min_log_diff > log10_max_diff:
                        self.params.slider_logarithmic = True

        auto_handle_format_and_logarithmic()

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


class _PossibleBoolAttributes(PossibleFiatAttributes):
    def __init__(self) -> None:
        super().__init__("BoolWithGui")
        self.add_explained_attribute(
            "edit_type", str, "Type of the edit widget. Possible values: checkbox, toggle", default_value="checkbox"
        )


_POSSIBLE_BOOL_ATTRIBUTES = _PossibleBoolAttributes()


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
    """A bool widget. Can use a checkbox or a toggle."""

    params: BoolWithGuiParams

    def __init__(self, params: BoolWithGuiParams | None = None):
        super().__init__(bool)
        self.params = params if params is not None else BoolWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: False
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.on_fiat_attributes_changed = self._handle_fiat_attrs
        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _POSSIBLE_BOOL_ATTRIBUTES

    def _handle_fiat_attrs(self, fiat_attrs: FiatAttributes) -> None:
        if "edit_type" in self.fiat_attributes:
            edit_type_ = self.fiat_attributes["edit_type"]
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
#                               ColorRbg and ColorRgba
########################################################################################################################


def _show_color_square(color: ImVec4) -> None:
    imgui.set_next_item_width(hello_imgui.em_size(10))
    imgui.color_button("##colorp", color, imgui.ColorEditFlags_.alpha_preview_half)


def _edit_color_rgb_float(value: ColorRgbFloat) -> tuple[bool, ColorRgbFloat]:
    if not isinstance(value, tuple):
        raise ValueError(f"ColorRgbWithGui expects a tuple, got: {type(value)}")
    if len(value) != 3:
        raise ValueError(f"ColorRgbWithGui expects a tuple of 3 floats, got: {value}")

    value_as_list = list(value)
    color_edit_flags = 0
    imgui.set_next_item_width(hello_imgui.em_size(10))
    changed, value_as_list = imgui.color_edit3("##color", value_as_list, color_edit_flags)

    if changed:
        r: ColorRgbFloat = tuple(value_as_list)  # type: ignore
        return True, r
    else:
        return False, value


def _edit_color_rgb(value: ColorRgb) -> tuple[bool, ColorRgb]:
    from fiatlight.fiat_types.color_types import color_rgb_to_color_rgb_float, color_rgb_float_to_color_rgb

    as_float = color_rgb_to_color_rgb_float(value)
    changed, as_float = _edit_color_rgb_float(as_float)
    if changed:
        r = color_rgb_float_to_color_rgb(as_float)
        return True, r
    else:
        return False, value


def _edit_color_rgba_float(value: ColorRgbaFloat) -> tuple[bool, ColorRgbaFloat]:
    if not isinstance(value, tuple):
        raise ValueError(f"ColorRgbaWithGui expects a tuple, got: {type(value)}")
    if len(value) != 4:
        raise ValueError(f"ColorRgbaWithGui expects a tuple of 4 floats, got: {value}")

    value_as_list = list(value)
    color_edit_flags = imgui.ColorEditFlags_.alpha_preview_half
    imgui.set_next_item_width(hello_imgui.em_size(14))
    changed, value_as_list = imgui.color_edit4("##color", value_as_list, color_edit_flags)

    if changed:
        r: ColorRgbaFloat = tuple(value_as_list)  # type: ignore
        return True, r
    else:
        return False, value


def _edit_color_rgba(value: ColorRgba) -> tuple[bool, ColorRgba]:
    from fiatlight.fiat_types.color_types import color_rgba_to_color_rgba_float, color_rgba_float_to_color_rgba

    as_float = color_rgba_to_color_rgba_float(value)
    changed, as_float = _edit_color_rgba_float(as_float)
    if changed:
        r = color_rgba_float_to_color_rgba(as_float)
        return True, r
    else:
        return False, value


def _present_color_rgb_str(value: ColorRgb) -> str:
    return f"R: {value[0]}, G: {value[1]}, B: {value[2]}"


def _present_color_rgb_gui(value: ColorRgb) -> None:
    from fiatlight.fiat_types.color_types import color_rgb_to_imvec4

    with imgui_ctx.begin_horizontal("##horizontal"):
        _show_color_square(color_rgb_to_imvec4(value))
        imgui.text(_present_color_rgb_str(value))


def _present_color_rgba_str(value: ColorRgba) -> str:
    return f"R: {value[0]}, G: {value[1]}, B: {value[2]}, A: {value[3]}"


def _present_color_rgba_gui(value: ColorRgba) -> None:
    from fiatlight.fiat_types.color_types import color_rgba_to_imvec4

    with imgui_ctx.begin_horizontal("##horizontal"):
        _show_color_square(color_rgba_to_imvec4(value))
        imgui.text(_present_color_rgba_str(value))


def _present_color_rgba_float_str(value: ColorRgbaFloat) -> str:
    return f"R: {value[0]:.3f}, G: {value[1]:.3f}, B: {value[2]:.3f}, A: {value[3]:.3f}"


def _present_color_rgba_float_gui(value: ColorRgbaFloat) -> None:
    from fiatlight.fiat_types.color_types import color_rgba_float_to_imvec4

    with imgui_ctx.begin_horizontal("##horizontal"):
        _show_color_square(color_rgba_float_to_imvec4(value))
        imgui.text(_present_color_rgba_float_str(value))


def present_color_rgb_float_str(value: ColorRgbFloat) -> str:
    return f"R: {value[0]:.3f}, G: {value[1]:.3f}, B: {value[2]:.3f}"


def _present_color_rgb_float_gui(value: ColorRgbFloat) -> None:
    from fiatlight.fiat_types.color_types import color_rgb_float_to_imvec4

    with imgui_ctx.begin_horizontal("##horizontal"):
        _show_color_square(color_rgb_float_to_imvec4(value))
        imgui.text(present_color_rgb_float_str(value))


class ColorRgbWithGui(AnyDataWithGui[ColorRgb]):
    """A nice color picker for RGB colors (int)"""

    def __init__(self) -> None:
        super().__init__(ColorRgb)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgb((0, 0, 0))
        self.callbacks.present_str = _present_color_rgb_str
        self.callbacks.present = _present_color_rgb_gui
        self.callbacks.present_collapsible = False
        self.callbacks.edit = _edit_color_rgb
        self.callbacks.edit_collapsible = False


class ColorRgbaWithGui(AnyDataWithGui[ColorRgba]):
    """A nice color picker for RGBA colors (int)"""

    def __init__(self) -> None:
        super().__init__(ColorRgba)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgba((0, 0, 0, 255))
        self.callbacks.present_str = _present_color_rgba_str
        self.callbacks.present = _present_color_rgba_gui
        self.callbacks.present_collapsible = False
        self.callbacks.edit = _edit_color_rgba
        self.callbacks.edit_collapsible = False


class ColorRgbaFloatWithGui(AnyDataWithGui[ColorRgbaFloat]):
    """A nice color picker for RGBA colors (float)"""

    def __init__(self) -> None:
        super().__init__(ColorRgbaFloat)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgbaFloat((0.0, 0.0, 0.0, 1.0))
        self.callbacks.present_str = _present_color_rgba_float_str
        self.callbacks.present = _present_color_rgba_float_gui
        self.callbacks.present_collapsible = False
        self.callbacks.edit = _edit_color_rgba_float
        self.callbacks.edit_collapsible = False


class ColorRgbFloatWithGui(AnyDataWithGui[ColorRgbFloat]):
    """A nice color picker for RGB colors (float)"""

    def __init__(self) -> None:
        super().__init__(ColorRgbFloat)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgbFloat((0.0, 0.0, 0.0))
        self.callbacks.present_str = present_color_rgb_float_str
        self.callbacks.edit = _edit_color_rgb_float
        self.callbacks.present = _present_color_rgb_float_gui
        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False
        self.callbacks.present_collapsible = False


########################################################################################################################
#                               Register all types
########################################################################################################################
def __register_python_types() -> None:
    from fiatlight.fiat_togui.gui_registry import register_type
    from .str_with_gui import StrWithGui

    register_type(int, IntWithGui)
    register_type(float, FloatWithGui)
    register_type(str, StrWithGui)
    register_type(bool, BoolWithGui)


def __register_color_types() -> None:
    from fiatlight.fiat_togui.gui_registry import register_typing_new_type

    register_typing_new_type(ColorRgb, ColorRgbWithGui)
    register_typing_new_type(ColorRgba, ColorRgbaWithGui)
    register_typing_new_type(ColorRgbFloat, ColorRgbFloatWithGui)
    register_typing_new_type(ColorRgbaFloat, ColorRgbaFloatWithGui)


def __register_custom_float_types() -> None:
    from fiatlight.fiat_togui.gui_registry import register_typing_new_type
    from fiatlight.fiat_types import PositiveFloat

    register_typing_new_type(PositiveFloat, make_positive_float_with_gui)


def _register_all_primitive_types() -> None:
    __register_python_types()
    __register_color_types()
    __register_custom_float_types()
