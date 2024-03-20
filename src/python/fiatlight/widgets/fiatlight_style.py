from imgui_bundle import ImVec4
from enum import Enum
from typing import Dict


class ColorType(Enum):
    InputPin = 0


COLORS: Dict[ColorType, ImVec4] = {
    ColorType.InputPin: ImVec4(0.4, 1.0, 0.4, 1.0),
}
