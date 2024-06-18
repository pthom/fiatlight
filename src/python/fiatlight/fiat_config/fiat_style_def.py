from enum import Enum, auto
from typing import Dict, Any
from dataclasses import dataclass

from pydantic import BaseModel, Field

from fiatlight.fiat_types.color_types import ColorRgbaFloat
from fiatlight.fiat_widgets.text_truncated import TruncationParams
from imgui_bundle import ImVec4, imgui_node_editor as ed


class FiatColorType(Enum):
    # Input Pins
    InputPinNotLinked = "InputPinNotLinked"
    InputPinLinked = "InputPinLinked"

    # Link
    LinkFunctions = "LinkFunctions"

    # Parameter value
    ParameterValueWithError = "ParameterValueWithError"
    ParameterValueLinked = "ParameterValueLinked"
    ParameterValueUsingDefault = "ParameterValueUsingDefault"
    ParameterValueUserSpecified = "ParameterValueUserSpecified"
    ParameterValueUnspecified = "ParameterValueUnspecified"

    # Output Pins
    OutputPinLinked = "OutputPinLinked"
    OutputPinNotLinked = "OutputPinNotLinked"

    # Output value
    ValueWithError = "ValueWithError"
    OutputValueDirty = "OutputValueDirty"
    ValueUnspecified = "ValueUnspecified"
    OutputValueOk = "OutputValueOk"

    DataclassMemberName = "DataclassMemberName"
    TupleLabel = "TupleLabel"

    # Exception color
    ExceptionError = "ExceptionError"

    InvalidValue = "InvalidValue"


class _ColorTypes(Enum):
    orange = auto()
    blue = auto()
    grey_blue = auto()
    green = auto()
    red = auto()
    grey = auto()
    transparent_grey = auto()
    yellow = auto()
    light_grey = auto()
    contrasting_black_or_white = auto()


@dataclass
class _ColorWithDarkLightVariations:
    dark_theme: ColorRgbaFloat
    light_theme: ColorRgbaFloat

    def __init__(self, dark_theme_color: ColorRgbaFloat, light_theme_color: ColorRgbaFloat | None = None):
        self.dark_theme = dark_theme_color
        self.light_theme = light_theme_color if light_theme_color is not None else dark_theme_color


_STANDARD_COLORS: dict[_ColorTypes, _ColorWithDarkLightVariations] = {
    _ColorTypes.orange: _ColorWithDarkLightVariations(
        ColorRgbaFloat((1.0, 0.8, 0.4, 1.0)), ColorRgbaFloat((0.8, 0.4, 0.0, 1.0))
    ),
    _ColorTypes.blue: _ColorWithDarkLightVariations(
        ColorRgbaFloat((0.5, 0.7, 1.0, 1.0)), ColorRgbaFloat((0.3, 0.4, 0.8, 1.0))
    ),
    _ColorTypes.grey_blue: _ColorWithDarkLightVariations(
        ColorRgbaFloat((0.6, 0.6, 0.65, 1.0)),
    ),
    _ColorTypes.green: _ColorWithDarkLightVariations(
        ColorRgbaFloat((0.4, 0.8, 0.4, 1.0)), ColorRgbaFloat((0.2, 0.6, 0.2, 1.0))
    ),
    _ColorTypes.red: _ColorWithDarkLightVariations(
        ColorRgbaFloat((1.0, 0.4, 0.4, 1.0)), ColorRgbaFloat((0.8, 0.2, 0.2, 1.0))
    ),
    _ColorTypes.grey: _ColorWithDarkLightVariations(
        ColorRgbaFloat((0.65, 0.65, 0.65, 1.0)), ColorRgbaFloat((0.35, 0.35, 0.35, 1.0))
    ),
    _ColorTypes.transparent_grey: _ColorWithDarkLightVariations(ColorRgbaFloat((0.8, 0.8, 0.8, 0.4))),
    _ColorTypes.yellow: _ColorWithDarkLightVariations(
        ColorRgbaFloat((1.0, 1.0, 0.0, 1.0)), ColorRgbaFloat((0.7, 0.7, 0.0, 1.0))
    ),
    _ColorTypes.light_grey: _ColorWithDarkLightVariations(ColorRgbaFloat((0.9, 0.9, 0.9, 1.0))),
    _ColorTypes.contrasting_black_or_white: _ColorWithDarkLightVariations(
        ColorRgbaFloat((1.0, 1.0, 1.0, 1.0)), ColorRgbaFloat((0.0, 0.0, 0.0, 1.0))
    ),
}


_STANDARD_COLORS_LIGHT_THEME: dict[_ColorTypes, ColorRgbaFloat] = {
    standard_color: value.light_theme for standard_color, value in _STANDARD_COLORS.items()
}

_STANDARD_COLORS_DARK_THEME: dict[_ColorTypes, ColorRgbaFloat] = {
    standard_color: value.dark_theme for standard_color, value in _STANDARD_COLORS.items()
}


class FiatStrTruncationParams(BaseModel):
    """FiatTextTruncation: Configuration for text truncation in the GUI"""

    # Header line (when presenting a value as a string)
    present_header_line: TruncationParams = TruncationParams(max_characters=40, max_lines=1)
    # Next lines (when presenting a value as a string, and expanded)
    present_next_lines: TruncationParams = TruncationParams(max_characters=40, max_lines=5)
    # When a string is presented in expanded mode inside a node
    str_expanded_in_node: TruncationParams = TruncationParams(max_characters=40, max_lines=5)
    # Invalid value message
    invalid_value_message: TruncationParams = TruncationParams(max_characters=40, max_lines=1)
    # Exceptions
    exceptions: TruncationParams = TruncationParams(max_characters=70, max_lines=7)


class FiatStyle(BaseModel):
    # colors used in the GUI
    colors: Dict[FiatColorType, ColorRgbaFloat] = Field(default_factory=dict)
    # minimum width of a node, in em units
    node_minimum_width_em: float = 9.0
    # max number of elements to display in node, for list-like data
    list_maximum_elements_in_node: int = 10

    # text truncation parameters
    str_truncation: FiatStrTruncationParams = FiatStrTruncationParams()

    # max width of the param labels, in em units
    # (if too big, they will be truncated and the full name will be displayed in a tooltip)
    param_label_max_width_em: float = 7.0
    # indentation between header line and edition / present
    indentation_em: float = 1.75

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.fill_with_default_style()

    def is_dark_theme(self) -> bool:
        if ed.get_current_editor() is None:
            return True

        node_bg_color = ed.get_style().color_(ed.StyleColor.node_bg)
        luminance = 0.2126 * node_bg_color.x + 0.7152 * node_bg_color.y + 0.0722 * node_bg_color.z
        is_dark = luminance < 0.5
        return is_dark

    def update_colors_from_imgui_colors(self) -> None:
        self.fill_with_default_style()

    def fill_with_default_style(self) -> None:
        is_dark_theme = self.is_dark_theme()
        colors = _STANDARD_COLORS_DARK_THEME if is_dark_theme else _STANDARD_COLORS_LIGHT_THEME
        default_colors = {
            # Input Pins
            FiatColorType.InputPinLinked: colors[_ColorTypes.blue],
            FiatColorType.InputPinNotLinked: colors[_ColorTypes.grey_blue],
            # Links
            FiatColorType.LinkFunctions: colors[_ColorTypes.contrasting_black_or_white],
            # Parameters
            FiatColorType.ParameterValueWithError: colors[_ColorTypes.red],
            FiatColorType.ParameterValueLinked: colors[_ColorTypes.blue],
            FiatColorType.ParameterValueUsingDefault: colors[_ColorTypes.grey],
            FiatColorType.ParameterValueUserSpecified: colors[_ColorTypes.green],
            FiatColorType.ParameterValueUnspecified: colors[_ColorTypes.orange],
            # Output Pins
            FiatColorType.OutputPinLinked: colors[_ColorTypes.blue],
            FiatColorType.OutputPinNotLinked: colors[_ColorTypes.grey_blue],
            # When the output is dirty
            FiatColorType.ValueWithError: colors[_ColorTypes.red],
            FiatColorType.OutputValueDirty: colors[_ColorTypes.orange],
            FiatColorType.ValueUnspecified: colors[_ColorTypes.red],
            FiatColorType.OutputValueOk: colors[_ColorTypes.contrasting_black_or_white],  # aaa
            # Dataclass member name
            FiatColorType.DataclassMemberName: ColorRgbaFloat((0.7, 0.8, 0.7, 1.0)),
            # Tuple label
            FiatColorType.TupleLabel: ColorRgbaFloat((0.7, 0.8, 0.7, 1.0)),
            # Exception color
            FiatColorType.ExceptionError: colors[_ColorTypes.red],
            # Invalid value
            FiatColorType.InvalidValue: colors[_ColorTypes.yellow],
        }

        for color_type, color in default_colors.items():
            self.colors[color_type] = color

    def color_as_vec4(self, color_type: FiatColorType) -> ImVec4:
        color = self.colors[color_type]
        return ImVec4(color[0], color[1], color[2], color[3])
