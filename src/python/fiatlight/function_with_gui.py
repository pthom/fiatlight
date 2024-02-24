from fiatlight.any_data_with_gui import AnyDataWithGui

from typing import Any, List, final, Callable, Optional
from dataclasses import dataclass


@dataclass
class NamedDataWithGui:
    name: str
    parameter_with_gui: AnyDataWithGui


class FunctionWithGui:
    """Instantiate this class with your functions, to make them available in a graph
    You need to provide:
    - the name of the function
    - the implementation of the function (f_impl)
    - the inputs and outputs of the function, as a list of NamedDataWithGui
    """

    # set this with the actual function implementation at construction time
    f_impl: Callable[..., Any] | None = None

    # the name of the function
    name: str

    # input_gui and output_gui should be filled during construction
    inputs_with_gui: List[NamedDataWithGui]
    outputs_with_gui: List[NamedDataWithGui]

    # if the last call raised an exception, the message is stored here
    last_exception_message: Optional[str] = None
    last_exception_traceback: Optional[str] = None

    def __init__(self) -> None:
        self.inputs_with_gui = []
        self.outputs_with_gui = []

    def all_inputs_ids(self) -> List[str]:
        return [param.name for param in self.inputs_with_gui]

    def all_outputs_ids(self) -> List[str]:
        return [param.name for param in self.outputs_with_gui]

    def input_of_name(self, name: str) -> AnyDataWithGui:
        for param in self.inputs_with_gui:
            if param.name == name:
                return param.parameter_with_gui
        assert False, f"input {name} not found"

    def output_of_name(self, name: str) -> AnyDataWithGui:
        for param in self.outputs_with_gui:
            if param.name == name:
                return param.parameter_with_gui
        assert False, f"output {name} not found"

    @final
    def invoke(self) -> Any:
        assert self.f_impl is not None
        values = [param.parameter_with_gui.value for param in self.inputs_with_gui]
        try:
            fn_output = self.f_impl(*values)
            if not isinstance(fn_output, tuple):
                assert len(self.outputs_with_gui) == 1
                self.outputs_with_gui[0].parameter_with_gui.value = fn_output
            else:
                assert len(fn_output) == len(self.outputs_with_gui)
                for i, output_with_gui in enumerate(self.outputs_with_gui):
                    output_with_gui.parameter_with_gui.value = fn_output[i]
            self.last_exception_message = None
            self.last_exception_traceback = None
        except Exception as e:
            self.last_exception_message = str(e)
            import traceback
            import sys

            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.last_exception_traceback = "".join(traceback_details)
            for output_with_gui in self.outputs_with_gui:
                output_with_gui.parameter_with_gui.value = None


class SourceWithGui(FunctionWithGui):
    """A source function that does not take any input and returns a user editable value"""

    def __init__(self, initial_value_with_gui: AnyDataWithGui, source_name: str = "Source") -> None:
        self.output_gui = initial_value_with_gui
        self.parameters_with_gui = [NamedDataWithGui("##source", initial_value_with_gui)]
        self.name = source_name

        def f(_: Any) -> Any:
            assert self.output_gui is not None
            return self.output_gui.value

        self.f_impl = f


__all__ = ["FunctionWithGui", "AnyDataWithGui", "NamedDataWithGui", "SourceWithGui"]
