from imgui_bundle import ImVec4
from enum import Enum
from typing import Dict


class ColorType(Enum):
    InputPin = 0
    InputPinUnspecified = 1
    InputPinWithError = 2
    #
    OutputPin = 3
    OutputPinUnspecified = 4
    OutputPinWithError = 5


COLORS: Dict[ColorType, ImVec4] = {
    ColorType.InputPin: ImVec4(0.4, 1.0, 0.4, 1.0),
    ColorType.InputPinUnspecified: ImVec4(1.0, 0.8, 0.4, 1.0),
    ColorType.InputPinWithError: ImVec4(1.0, 0.5, 0.4, 1.0),
    ColorType.OutputPin: ImVec4(0.4, 0.4, 1.0, 1.0),
    ColorType.OutputPinUnspecified: ImVec4(0.8, 0.4, 1.0, 1.0),
    ColorType.OutputPinWithError: ImVec4(1.0, 0.4, 0.4, 1.0),
}
