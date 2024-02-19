from fiatlight.f2.function_with_settable_params import FunctionWithSettableParams

from typing import Any, TypeVar, Optional, Generic
import sys
import traceback


Input = TypeVar("Input")
Output = TypeVar("Output")


class FunctionContainer(Generic[Input, Output]):
    """A class that represents a function and its input and output.
    It stores the input and output of the function, as well as optional parameters
    It recomputes the output when the input is modified, or when the parameters are modified.

    It also stores the last exception message and traceback, if the function raised an exception.
    """

    _function: FunctionWithSettableParams[Input, Output]
    _input: Input | None
    _output: Output | None

    last_exception_message: Optional[str] = None
    last_exception_traceback: Optional[str] = None

    def __init__(self, f: FunctionWithSettableParams[Input, Output]) -> None:
        self._function = f
        self._input = None
        self._output = None
        self.name = f.name()

    def _compute_output(self) -> None:
        if self._input is None:
            self._output = None
            return
        try:
            r = self._function(self._input)
            self._output = r
            self.last_exception_message = None
            self.last_exception_traceback = None
        except Exception as e:
            self.last_exception_message = str(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.last_exception_traceback = "".join(traceback_details)
            self._output = None

    def __call__(self, v: Input) -> Output | None:
        self.set_input(v)
        return self.get_output()

    def set_input(self, value: Any) -> None:
        self._input = value
        self._compute_output()

    def get_input(self) -> Input | None:
        return self._input

    def get_output(self) -> Output | None:
        return self._output


# def sandbox1() -> None:
#     def f(a: int) -> int:
#         return a + 3
#
#     # obs_f = FunctionContainer(math.log)
#     obs_f = FunctionContainer(f)
#     obs_f.set_input(3)
#     print(obs_f.get_input())
#     print(obs_f.get_output())
#     # print(obs_f.signature())
#     # print(obs_f.nb_params())
#
#
# if __name__ == "__main__":
#     sandbox1()
