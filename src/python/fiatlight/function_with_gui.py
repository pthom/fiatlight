from fiatlight.any_data_with_gui import AnyDataWithGui

from typing import Any, List
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FunctionParameterWithGui:
    name: str
    parameter_with_gui: AnyDataWithGui


class DummySource:
    pass


class FunctionWithGui(ABC):
    """Override this class with your functions which you want to visualize in a graph
    // FunctionWithGui: any function that can be presented visually, with
    // - a displayed name
    // - a gui in order to modify the internal params
    // - a pure function f: AnyDataWithGui -> AnyDataWithGui
    """

    # input_gui and output_gui should be filled during construction
    input_gui: AnyDataWithGui | None = None
    output_gui: AnyDataWithGui | None = None

    # parameters_with_gui should be filled during construction
    parameters_with_gui: List[FunctionParameterWithGui] | None = None

    @abstractmethod
    def f(self, x: Any) -> Any:
        """override this with the actual function implementation"""
        pass

    @abstractmethod
    def name(self) -> str:
        """override this with the actual function name"""
        pass

    def old_gui_params(self) -> bool:
        """override this if you want to provide a gui for the function inner params
        (i.e. neither input nor output params, but the function internal state)
        It should return True if the inner params were changed.
        """
        return False


class SourceWithGui(FunctionWithGui):
    """A source function that does not take any input and returns a user editable value"""

    source_name: str = "Source"

    def __init__(self, initial_value_with_gui: AnyDataWithGui, source_name: str = "Source") -> None:
        self.output_gui = initial_value_with_gui
        self.parameters_with_gui = [FunctionParameterWithGui("source", initial_value_with_gui)]
        self.source_name = source_name

    def f(self, _: DummySource) -> Any:
        assert self.output_gui is not None
        return self.output_gui.value

    def name(self) -> str:
        return self.source_name


__all__ = ["FunctionWithGui", "AnyDataWithGui"]
