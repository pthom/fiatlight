from imgui_bundle import ImVec4
from enum import Enum, auto
from typing import Dict


class FiatColorType(Enum):
    # Input Pins
    InputPinNotLinked = auto()
    InputPinLinked = auto()

    # Parameter value
    ParameterValueWithError = auto()
    ParameterValueLinked = auto()
    ParameterValueUsingDefault = auto()
    ParameterValueUserSpecified = auto()
    ParameterValueUnspecified = auto()

    # Output Pins
    OutputPinLinked = auto()
    OutputPinNotLinked = auto()

    # Output value
    OutputValueWithError = auto()
    OutputValueDirty = auto()
    OutputValueUnspecified = auto()
    OutputValueOk = auto()

    # Exception color
    ExceptionError = auto()


class FiatStyle:
    colors: Dict[FiatColorType, ImVec4]

    # Named colors for better readability
    orange = ImVec4(1.0, 0.8, 0.4, 1.0)
    blue = ImVec4(0.5, 0.7, 1.0, 1.0)
    grey_blue = ImVec4(0.6, 0.6, 0.65, 1.0)
    green = ImVec4(0.4, 0.8, 0.4, 1.0)
    red = ImVec4(1.0, 0.4, 0.4, 1.0)
    grey = ImVec4(0.5, 0.5, 0.5, 1.0)
    transparent_grey = ImVec4(0.8, 0.8, 0.8, 0.4)
    white = ImVec4(1.0, 1.0, 1.0, 1.0)

    node_minimum_width_em: float = 9.0

    list_maximum_elements_in_node: int = 10

    def __init__(self) -> None:
        self.colors = {
            # Input Pins
            FiatColorType.InputPinLinked: self.blue,
            FiatColorType.InputPinNotLinked: self.grey_blue,
            # Parameters
            FiatColorType.ParameterValueWithError: self.red,
            FiatColorType.ParameterValueLinked: self.blue,
            FiatColorType.ParameterValueUserSpecified: self.green,
            FiatColorType.ParameterValueUnspecified: self.orange,
            FiatColorType.ParameterValueUsingDefault: self.grey,
            # Output Pins
            FiatColorType.OutputPinLinked: self.blue,
            FiatColorType.OutputPinNotLinked: self.grey_blue,
            # When the output is dirty
            FiatColorType.OutputValueDirty: self.orange,
            FiatColorType.OutputValueWithError: self.red,
            FiatColorType.OutputValueUnspecified: self.red,
            FiatColorType.OutputValueOk: self.white,
            # Exception color
            FiatColorType.ExceptionError: self.red,
        }
