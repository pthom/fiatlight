from imgui_bundle import ImVec4
from enum import Enum
from typing import Dict


class FiatColorType(Enum):
    InputPin = 0
    InputPinUnspecified = 1
    InputPinWithError = 2
    #
    OutputPin = 3
    OutputPinUnspecified = 4
    OutputPinWithError = 5
    #
    TextDirtyOutput = 6


class FiatStyle:
    colors: Dict[FiatColorType, ImVec4]

    node_minimum_width_em: float = 9.0

    list_maximum_elements_in_node: int = 10

    def __init__(self) -> None:
        self.colors = {
            FiatColorType.InputPin: ImVec4(0.4, 1.0, 0.4, 1.0),
            FiatColorType.InputPinUnspecified: ImVec4(1.0, 0.8, 0.4, 1.0),
            FiatColorType.InputPinWithError: ImVec4(1.0, 0.5, 0.4, 1.0),
            FiatColorType.OutputPin: ImVec4(0.4, 0.4, 1.0, 1.0),
            FiatColorType.OutputPinUnspecified: ImVec4(0.8, 0.4, 1.0, 1.0),
            FiatColorType.OutputPinWithError: ImVec4(1.0, 0.4, 0.4, 1.0),
            FiatColorType.TextDirtyOutput: ImVec4(0.8, 0.8, 0.8, 0.4),
        }
