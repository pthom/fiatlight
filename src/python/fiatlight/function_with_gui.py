from fiatlight.any_data_with_gui import AnyDataWithGui

from typing import Any, List, final, Callable, TypeVar, Generic
from dataclasses import dataclass


@dataclass
class FunctionParameterWithGui:
    name: str
    parameter_with_gui: AnyDataWithGui


class DummySource:
    pass


Input = TypeVar("Input")
Output = TypeVar("Output")


class FunctionWithGui(Generic[Input, Output]):
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

    # the name of the function
    name: str

    # set this with the actual function implementation at construction time
    f_impl: Callable[[Input], Output] | None = None

    @final
    def f(self, x: Input) -> Output:
        assert self.f_impl is not None
        return self.f_impl(x)

    def old_gui_params(self) -> bool:
        """override this if you want to provide a gui for the function inner params
        (i.e. neither input nor output params, but the function internal state)
        It should return True if the inner params were changed.
        """
        return False


class SourceWithGui(FunctionWithGui[DummySource, Any]):
    """A source function that does not take any input and returns a user editable value"""

    def __init__(self, initial_value_with_gui: AnyDataWithGui, source_name: str = "Source") -> None:
        self.output_gui = initial_value_with_gui
        self.parameters_with_gui = [FunctionParameterWithGui("source", initial_value_with_gui)]
        self.name = source_name

        def f(_: Any) -> Any:
            assert self.output_gui is not None
            return self.output_gui.value

        self.f_impl = f


__all__ = ["FunctionWithGui", "AnyDataWithGui"]
