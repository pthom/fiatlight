from imgui_bundle import imgui, hello_imgui, imgui_knobs, imgui_toggle, ImVec2, imgui_ctx, ImVec4
from fiatlight.fiat_core import AnyDataWithGui, PossibleCustomAttributes
from fiatlight.fiat_types.color_types import ColorRgb, ColorRgba, ColorRgbFloat, ColorRgbaFloat
from fiatlight.fiat_types import CustomAttributesDict
from typing import Callable, TypeAlias
from dataclasses import dataclass
from enum import Enum


GuiFunction = Callable[[], None]


########################################################################################################################
#                               Ints
########################################################################################################################
ImGuiKnobVariant_: TypeAlias = imgui_knobs.ImGuiKnobVariant_
ToggleConfig: TypeAlias = imgui_toggle.ToggleConfig


class _PossibleIntAttributes(PossibleCustomAttributes):
    def __init__(self) -> None:
        super().__init__("IntWithGui")
        self.add_explained_attribute("range", tuple, "Range of the integer", "(int, int)")
        self.add_explained_attribute(
            "edit_type",
            str,
            "Type of the edit widget. Possible values: slider, input, drag, knob, slider_and_minus_plus",
        )
        self.add_explained_attribute("format", str, "Format string for the value")
        self.add_explained_attribute("width_em", float, "Width of the widget in em")
        self.add_explained_attribute("knob_size_em", float, "Size of the knob in em")
        self.add_explained_attribute("knob_steps", int, "Number of steps in the knob")
        self.add_explained_attribute("knob_no_input", bool, "Disable text input on knobs and sliders")
        self.add_explained_attribute("slider_no_input", bool, "Disable text input on sliders")
        self.add_explained_attribute("slider_logarithmic", bool, "Use a logarithmic scale for sliders")


_POSSIBLE_INT_ATTRIBUTES = _PossibleIntAttributes()


def int_custom_attributes_documentation() -> str:
    return _POSSIBLE_INT_ATTRIBUTES.documentation()


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
    """A highly customizable int widget."""

    params: IntWithGuiParams

    def __init__(self, params: IntWithGuiParams | None = None) -> None:
        super().__init__(int)
        self.params = params if params is not None else IntWithGuiParams()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: 0
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.on_custom_attrs_changed = self._handle_custom_attrs

    def _handle_custom_attrs(self, custom_attrs: CustomAttributesDict) -> None:
        _POSSIBLE_INT_ATTRIBUTES.raise_exception_if_bad_custom_attrs(custom_attrs)
        if "range" in self.custom_attrs:
            range_ = self.custom_attrs["range"]
            self.params.v_min = range_[0]
            self.params.v_max = range_[1]
            self.params.edit_type = IntEditType.slider

        if "edit_type" in self.custom_attrs:
            edit_type_ = self.custom_attrs["edit_type"]
            try:
                edit_type = IntEditType[edit_type_]
                self.params.edit_type = edit_type
            except KeyError:
                raise ValueError(f"Unknown edit_type: {edit_type_}. Available types: {available_int_edit_types()}")

        if "format" in self.custom_attrs:
            self.params.format = self.custom_attrs["format"]

        if "width_em" in self.custom_attrs:
            if not isinstance(self.custom_attrs["width_em"], (int, float)):
                raise ValueError(f"width_em must be a number, got: {self.custom_attrs['width_em']}")
            self.params.width_em = self.custom_attrs["width_em"]

        if "knob_size_em" in self.custom_attrs:
            if not isinstance(self.custom_attrs["knob_size_em"], (int, float)):
                raise ValueError(f"knob_size_em must be a number, got: {self.custom_attrs['knob_size_em']}")
            self.params.knob_size_em = self.custom_attrs["knob_size_em"]

        if "knob_steps" in self.custom_attrs:
            if not isinstance(self.custom_attrs["knob_steps"], int):
                raise ValueError(f"knob_steps must be an integer, got: {self.custom_attrs['knob_steps']}")
            self.params.knob_steps = self.custom_attrs["knob_steps"]

        if "knob_no_input" in self.custom_attrs:
            if not isinstance(self.custom_attrs["knob_no_input"], bool):
                raise ValueError(f"knob_no_input must be a boolean, got: {self.custom_attrs['knob_no_input']}")
            self.params.knob_no_input = self.custom_attrs["knob_no_input"]

        if "slider_no_input" in self.custom_attrs:
            if not isinstance(self.custom_attrs["slider_no_input"], bool):
                raise ValueError(f"slider_no_input must be a boolean, got: {self.custom_attrs['slider_no_input']}")
            self.params.slider_no_input = self.custom_attrs["slider_no_input"]

        if "slider_logarithmic" in self.custom_attrs:
            if not isinstance(self.custom_attrs["slider_logarithmic"], bool):
                raise ValueError(
                    f"slider_logarithmic must be a boolean, got: {self.custom_attrs['slider_logarithmic']}"
                )
            self.params.slider_logarithmic = self.custom_attrs["slider_logarithmic"]

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


class PossibleFloatAttributes(PossibleCustomAttributes):
    def __init__(self) -> None:
        super().__init__("FloatWithGui")
        self.add_explained_attribute("range", tuple, "Range of the float", "(float, float)")
        self.add_explained_attribute(
            "edit_type",
            str,
            "Type of the edit widget. Possible values: slider, input, drag, knob, slider_float_any_range, slider_float_any_range_positive",
        )
        self.add_explained_attribute("format", str, "Format string for the value")
        self.add_explained_attribute("width_em", float, "Width of the widget in em")
        self.add_explained_attribute("knob_size_em", float, "Size of the knob in em")
        self.add_explained_attribute("knob_steps", int, "Number of steps in the knob")
        self.add_explained_attribute("knob_no_input", bool, "Disable text input on knobs and sliders")
        self.add_explained_attribute("slider_no_input", bool, "Disable text input on sliders")
        self.add_explained_attribute("slider_logarithmic", bool, "Use a logarithmic scale for sliders")


_POSSIBLE_FLOAT_ATTRIBUTES = PossibleFloatAttributes()


def float_custom_attributes_documentation() -> str:
    return _POSSIBLE_FLOAT_ATTRIBUTES.documentation()


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
        self.callbacks.on_custom_attrs_changed = self._handle_custom_attrs

    def _handle_custom_attrs(self, custom_attrs: CustomAttributesDict) -> None:
        _POSSIBLE_FLOAT_ATTRIBUTES.raise_exception_if_bad_custom_attrs(custom_attrs)
        if "range" in self.custom_attrs:
            range_ = self.custom_attrs["range"]
            if not isinstance(range_, tuple) or len(range_) != 2:
                raise ValueError(f"range must be a tuple of two numbers, got: {range_}")
            if not all(isinstance(x, (int, float)) for x in range_):
                raise ValueError(f"range must be a tuple of two numbers, got: {range_}")
            self.params.v_min = range_[0]
            self.params.v_max = range_[1]
            self.params.edit_type = FloatEditType.slider

        if "edit_type" in self.custom_attrs:
            edit_type_ = self.custom_attrs["edit_type"]
            try:
                edit_type = FloatEditType[edit_type_]
                self.params.edit_type = edit_type
                if edit_type == FloatEditType.knob:
                    self.params.format = "%.2f"
            except KeyError:
                raise ValueError(f"Unknown edit_type: {edit_type_}. Available types: {_available_float_edit_types()}")

        if "format" in self.custom_attrs:
            self.params.format = self.custom_attrs["format"]

        if "width_em" in self.custom_attrs:
            if not isinstance(self.custom_attrs["width_em"], (int, float)):
                raise ValueError(f"width_em must be a number, got: {self.custom_attrs['width_em']}")
            self.params.width_em = self.custom_attrs["width_em"]

        if "knob_size_em" in self.custom_attrs:
            if not isinstance(self.custom_attrs["knob_size_em"], (int, float)):
                raise ValueError(f"knob_size_em must be a number, got: {self.custom_attrs['knob_size_em']}")
            self.params.knob_size_em = self.custom_attrs["knob_size_em"]

        if "knob_steps" in self.custom_attrs:
            if not isinstance(self.custom_attrs["knob_steps"], int):
                raise ValueError(f"knob_steps must be an integer, got: {self.custom_attrs['knob_steps']}")
            self.params.knob_steps = self.custom_attrs["knob_steps"]

        if "knob_no_input" in self.custom_attrs:
            if not isinstance(self.custom_attrs["knob_no_input"], bool):
                raise ValueError(f"knob_no_input must be a boolean, got: {self.custom_attrs['knob_no_input']}")
            self.params.knob_no_input = self.custom_attrs["knob_no_input"]

        if "slider_no_input" in self.custom_attrs:
            if not isinstance(self.custom_attrs["slider_no_input"], bool):
                raise ValueError(f"slider_no_input must be a boolean, got: {self.custom_attrs['slider_no_input']}")
            self.params.slider_no_input = self.custom_attrs["slider_no_input"]

        if "slider_logarithmic" in self.custom_attrs:
            if not isinstance(self.custom_attrs["slider_logarithmic"], bool):
                raise ValueError(
                    f"slider_logarithmic must be a boolean, got: {self.custom_attrs['slider_logarithmic']}"
                )
            self.params.slider_logarithmic = self.custom_attrs["slider_logarithmic"]

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


class _PossibleBoolAttributes(PossibleCustomAttributes):
    def __init__(self) -> None:
        super().__init__("BoolWithGui")
        self.add_explained_attribute("edit_type", str, "Type of the edit widget. Possible values: checkbox, toggle")


_POSSIBLE_BOOL_ATTRIBUTES = _PossibleBoolAttributes()


def bool_custom_attributes_documentation() -> str:
    return _POSSIBLE_BOOL_ATTRIBUTES.documentation()


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
        self.callbacks.on_custom_attrs_changed = self._handle_custom_attrs

    def _handle_custom_attrs(self, custom_attrs: CustomAttributesDict) -> None:
        _POSSIBLE_BOOL_ATTRIBUTES.raise_exception_if_bad_custom_attrs(custom_attrs)
        if "edit_type" in self.custom_attrs:
            edit_type_ = self.custom_attrs["edit_type"]
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


def _edit_color_rgb_float(value: ColorRgbFloat) -> tuple[bool, ColorRgbFloat]:
    if not isinstance(value, tuple):
        raise ValueError(f"ColorRgbWithGui expects a tuple, got: {type(value)}")
    if len(value) != 3:
        raise ValueError(f"ColorRgbWithGui expects a tuple of 3 floats, got: {value}")

    value_as_list = list(value)
    picker_flags_std = imgui.ColorEditFlags_.no_side_preview.value
    picker_flags_wheel = imgui.ColorEditFlags_.picker_hue_wheel.value | imgui.ColorEditFlags_.no_inputs.value

    imgui.set_next_item_width(hello_imgui.em_size(8))
    changed1, value_as_list = imgui.color_picker3("##color", value_as_list, picker_flags_std)
    imgui.same_line()
    imgui.set_next_item_width(hello_imgui.em_size(8))
    changed2, value_as_list = imgui.color_picker3("##color", value_as_list, picker_flags_wheel)
    changed = changed1 or changed2

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
    value_as_imvec4 = ImVec4(value[0], value[1], value[2], value[3])

    imgui.text("Edit")

    picker_flags_std = imgui.ColorEditFlags_.no_side_preview.value | imgui.ColorEditFlags_.alpha_preview_half.value
    picker_flags_wheel = (
        imgui.ColorEditFlags_.picker_hue_wheel.value
        | imgui.ColorEditFlags_.no_inputs.value
        | imgui.ColorEditFlags_.alpha_preview_half.value
    )

    imgui.set_next_item_width(hello_imgui.em_size(8))
    changed1, value_as_imvec4 = imgui.color_picker4("##color", value_as_imvec4, picker_flags_std)
    imgui.same_line()
    imgui.set_next_item_width(hello_imgui.em_size(8))
    changed2, value_as_imvec4 = imgui.color_picker4("##color", value_as_imvec4, picker_flags_wheel)
    if changed1 or changed2:
        r: ColorRgbaFloat = (value_as_imvec4.x, value_as_imvec4.y, value_as_imvec4.z, value_as_imvec4.w)  # type: ignore  # noqa
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


def _present_color_rgb(value: ColorRgb) -> str:
    return f"R: {value[0]}, G: {value[1]}, B: {value[2]}"


def _present_color_rgba(value: ColorRgba) -> str:
    return f"R: {value[0]}, G: {value[1]}, B: {value[2]}, A: {value[3]}"


def _present_color_rgba_float(value: ColorRgbaFloat) -> str:
    return f"R: {value[0]:.3f}, G: {value[1]:.3f}, B: {value[2]:.3f}, A: {value[3]:.3f}"


def present_color_rgb_float(value: ColorRgbFloat) -> str:
    return f"R: {value[0]:.3f}, G: {value[1]:.3f}, B: {value[2]:.3f}"


class ColorRgbWithGui(AnyDataWithGui[ColorRgb]):
    """A nice color picker for RGB colors (int)"""

    def __init__(self) -> None:
        super().__init__(ColorRgb)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgb((0, 0, 0))
        self.callbacks.present_str = _present_color_rgb
        self.callbacks.edit = _edit_color_rgb


class ColorRgbaWithGui(AnyDataWithGui[ColorRgba]):
    """A nice color picker for RGBA colors (int)"""

    def __init__(self) -> None:
        super().__init__(ColorRgba)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgba((0, 0, 0, 255))
        self.callbacks.present_str = _present_color_rgba
        self.callbacks.edit = _edit_color_rgba


class ColorRgbaFloatWithGui(AnyDataWithGui[ColorRgbaFloat]):
    """A nice color picker for RGBA colors (float)"""

    def __init__(self) -> None:
        super().__init__(ColorRgbaFloat)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgbaFloat((0.0, 0.0, 0.0, 1.0))
        self.callbacks.present_str = _present_color_rgba_float
        self.callbacks.edit = _edit_color_rgba_float


class ColorRgbFloatWithGui(AnyDataWithGui[ColorRgbFloat]):
    """A nice color picker for RGB colors (float)"""

    def __init__(self) -> None:
        super().__init__(ColorRgbFloat)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.default_value_provider = lambda: ColorRgbFloat((0.0, 0.0, 0.0))
        self.callbacks.present_str = present_color_rgb_float
        self.callbacks.edit = _edit_color_rgb_float


########################################################################################################################
#                               Register all types
########################################################################################################################
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
    register_type(ColorRgbFloat, ColorRgbFloatWithGui)
    register_type(ColorRgbaFloat, ColorRgbaFloatWithGui)


def __register_custom_float_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_types import PositiveFloat

    register_type(PositiveFloat, make_positive_float_with_gui)


def _register_all_primitive_types() -> None:
    __register_python_types()
    __register_color_types()
    __register_custom_float_types()
