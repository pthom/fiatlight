from imgui_bundle import ImVec4
from enum import Enum
from typing import Dict


class GuiColorType(Enum):
    InputPin = 0
    InputPinUnspecified = 1
    InputPinWithError = 2
    #
    OutputPin = 3
    OutputPinUnspecified = 4
    OutputPinWithError = 5
    #
    TextDirtyOutput = 6


class FiatlightStyle:
    colors: Dict[GuiColorType, ImVec4]

    node_minimum_width_em: float = 9.0

    list_maximum_elements_in_node: int = 10

    def __init__(self) -> None:
        self.colors = {
            GuiColorType.InputPin: ImVec4(0.4, 1.0, 0.4, 1.0),
            GuiColorType.InputPinUnspecified: ImVec4(1.0, 0.8, 0.4, 1.0),
            GuiColorType.InputPinWithError: ImVec4(1.0, 0.5, 0.4, 1.0),
            GuiColorType.OutputPin: ImVec4(0.4, 0.4, 1.0, 1.0),
            GuiColorType.OutputPinUnspecified: ImVec4(0.8, 0.4, 1.0, 1.0),
            GuiColorType.OutputPinWithError: ImVec4(1.0, 0.4, 0.4, 1.0),
            GuiColorType.TextDirtyOutput: ImVec4(0.8, 0.8, 0.8, 0.4),
        }


_FIATLIGHT_STYLE = FiatlightStyle()


def fiatlight_style() -> FiatlightStyle:
    return _FIATLIGHT_STYLE
