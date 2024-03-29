from imgui_bundle import ImVec4
from enum import Enum, auto
from typing import Dict


class FiatColorType(Enum):
    # Input Pins
    InputPinNotLinked = auto()
    InputPinLinked = auto()

    # Parameters
    ParameterWithError = auto()
    ParameterLinked = auto()
    ParameterUsingDefault = auto()
    ParameterUserSpecified = auto()
    ParameterUnspecified = auto()

    # Output Pins
    OutputPin = auto()
    OutputPinUnspecified = auto()
    OutputPinWithError = auto()

    # When the output is dirty
    TextDirtyOutput = auto

    # Exception color
    ExceptionError = auto()


class FiatStyle:
    colors: Dict[FiatColorType, ImVec4]

    node_minimum_width_em: float = 9.0

    list_maximum_elements_in_node: int = 10

    def __init__(self) -> None:
        self.colors = {
            # Input Pins
            FiatColorType.InputPinLinked: ImVec4(0.3, 0.6, 1.0, 1.0),
            FiatColorType.InputPinNotLinked: ImVec4(0.4, 0.8, 0.4, 1.0),
            # Parameters
            FiatColorType.ParameterWithError: ImVec4(1.0, 0.4, 0.4, 1.0),
            FiatColorType.ParameterLinked: ImVec4(0.3, 0.6, 1.0, 1.0),
            FiatColorType.ParameterUserSpecified: ImVec4(0.4, 1.0, 0.4, 1.0),
            FiatColorType.ParameterUnspecified: ImVec4(1.0, 0.8, 0.4, 1.0),
            FiatColorType.ParameterUsingDefault: ImVec4(0.5, 0.5, 0.5, 1.0),
            # Output Pins
            FiatColorType.OutputPin: ImVec4(0.4, 0.4, 1.0, 1.0),
            FiatColorType.OutputPinUnspecified: ImVec4(1.0, 0.8, 0.4, 1.0),
            FiatColorType.OutputPinWithError: ImVec4(1.0, 0.4, 0.4, 1.0),
            # When the output is dirty
            FiatColorType.TextDirtyOutput: ImVec4(0.8, 0.8, 0.8, 0.4),
            # Exception color
            FiatColorType.ExceptionError: ImVec4(1.0, 0.4, 0.4, 1.0),
        }
