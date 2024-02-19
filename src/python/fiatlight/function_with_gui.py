from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.parameter_with_gui import ParameterWithGui

from typing import Any, List
from abc import ABC, abstractmethod


class FunctionWithGui(ABC):
    """Override this class with your functions which you want to visualize in a graph
    // FunctionWithGui: any function that can be presented visually, with
    // - a displayed name
    // - a gui in order to modify the internal params
    // - a pure function f: AnyDataWithGui -> AnyDataWithGui
    """

    # input_gui and output_gui should be filled during construction
    input_gui: AnyDataWithGui
    output_gui: AnyDataWithGui

    # parameters_with_gui should be filled during construction
    parameters_with_gui: List[ParameterWithGui[Any]] | None = None

    @abstractmethod
    def f(self, x: Any) -> Any:
        """override this with the actual function implementation"""
        pass

    @abstractmethod
    def name(self) -> str:
        """override this with the actual function name"""
        pass

    def gui_params(self) -> bool:
        """override this if you want to provide a gui for the function inner params
        (i.e. neither input nor output params, but the function internal state)
        It should return True if the inner params were changed.
        """
        return False


__all__ = ["FunctionWithGui", "ParameterWithGui", "AnyDataWithGui"]
