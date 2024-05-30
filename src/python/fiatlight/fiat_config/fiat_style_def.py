from enum import Enum
from typing import Dict, Any

from pydantic import BaseModel, Field

from fiatlight.fiat_types.color_types import ColorRgbaFloat
from imgui_bundle import ImVec4


class FiatColorType(Enum):
    # Input Pins
    InputPinNotLinked = "InputPinNotLinked"
    InputPinLinked = "InputPinLinked"

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
    OutputValueWithError = "OutputValueWithError"
    OutputValueDirty = "OutputValueDirty"
    OutputValueUnspecified = "OutputValueUnspecified"
    OutputValueOk = "OutputValueOk"

    DataclassMemberName = "DataclassMemberName"

    # Exception color
    ExceptionError = "ExceptionError"

    InvalidValue = "InvalidValue"


orange = ColorRgbaFloat((1.0, 0.8, 0.4, 1.0))
blue = ColorRgbaFloat((0.5, 0.7, 1.0, 1.0))
grey_blue = ColorRgbaFloat((0.6, 0.6, 0.65, 1.0))
green = ColorRgbaFloat((0.4, 0.8, 0.4, 1.0))
red = ColorRgbaFloat((1.0, 0.4, 0.4, 1.0))
grey = ColorRgbaFloat((0.5, 0.5, 0.5, 1.0))
transparent_grey = ColorRgbaFloat((0.8, 0.8, 0.8, 0.4))
white = ColorRgbaFloat((1.0, 1.0, 1.0, 1.0))
yellow = ColorRgbaFloat((1.0, 1.0, 0.0, 1.0))


class FiatStyle(BaseModel):
    colors: Dict[FiatColorType, ColorRgbaFloat] = Field(default_factory=dict)
    node_minimum_width_em: float = 9.0
    list_maximum_elements_in_node: int = 10

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.fill_with_default_style()

    def fill_with_default_style(self) -> None:
        default_colors = {
            # Input Pins
            FiatColorType.InputPinLinked: blue,
            FiatColorType.InputPinNotLinked: grey_blue,
            # Parameters
            FiatColorType.ParameterValueWithError: red,
            FiatColorType.ParameterValueLinked: blue,
            FiatColorType.ParameterValueUsingDefault: grey,
            FiatColorType.ParameterValueUserSpecified: green,
            FiatColorType.ParameterValueUnspecified: orange,
            # Output Pins
            FiatColorType.OutputPinLinked: blue,
            FiatColorType.OutputPinNotLinked: grey_blue,
            # When the output is dirty
            FiatColorType.OutputValueWithError: red,
            FiatColorType.OutputValueDirty: orange,
            FiatColorType.OutputValueUnspecified: red,
            FiatColorType.OutputValueOk: white,
            # Dataclass member name
            FiatColorType.DataclassMemberName: ColorRgbaFloat((0.7, 0.8, 0.7, 1.0)),
            # Exception color
            FiatColorType.ExceptionError: red,
            # Invalid value
            FiatColorType.InvalidValue: yellow,
        }

        # fill missing colors
        for color_type, color in default_colors.items():
            if color_type not in self.colors:
                self.colors[color_type] = color

    def color_as_vec4(self, color_type: FiatColorType) -> ImVec4:
        color = self.colors[color_type]
        return ImVec4(color[0], color[1], color[2], color[3])


def test_serialize_style() -> None:
    style = FiatStyle()
    style.colors[FiatColorType.OutputValueOk] = red

    as_json = style.model_dump(mode="json")

    style2 = FiatStyle.model_validate(as_json)
    assert style == style2

    print(style.colors[FiatColorType.OutputValueOk])
    print(style2.colors[FiatColorType.OutputValueOk])
