from typing import Any
from abc import ABC, abstractmethod
from fiatlux.any_data_with_gui import AnyDataWithGui


class FunctionWithGui(ABC):
    """Override this class with your functions which you want to vizualize in a graph
    // FunctionWithGui: any function that can be presented visually, with
    // - a displayed name
    // - a gui in order to modify the internal params
    // - a pure function f: AnyDataWithGui -> AnyDataWithGui
    """

    # input_gui and output_gui should be filled during construction
    input_gui: AnyDataWithGui
    output_gui: AnyDataWithGui

    @abstractmethod
    def f(self, x: Any) -> Any:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def gui_params(self) -> bool:
        """override this if you want to provide a gui for the function inner params
        (i.e. neither input nor output params, but the function internal state)
        It should return True if the inner params were changed.
        """
        return False
