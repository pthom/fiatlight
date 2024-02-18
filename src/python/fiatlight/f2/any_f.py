from typing import Any, Tuple, Callable, TypeAlias, TypeVar, Optional, Generic
from fiatlight.fiatlight_types import PureFunction
import inspect
import sys
import traceback


T = TypeVar("T")
Input = TypeVar("Input")
Output = TypeVar("Output")


# Observer: TypeAlias = Callable[[Any], None]

# Any function that can present an editable GUI for a given data, and return (changed, new_value)
EditDataGuiFunction: TypeAlias = Callable[[T | None], Tuple[bool, T]]

# Any function that can present a non-editable GUI for a given data
PresentDataGuiFunction: TypeAlias = Callable[[T | None], None]

# Any function that can create a default value for a given data type
DefaultValueProvider: TypeAlias = Callable[[], T]


class ObservableData(Generic[T]):
    """A class that can store a value, and can be observed by other classes.
    It is used to store the input and output of functions.
    """

    _value: T | None

    def __init__(self, value: T | None = None) -> None:
        self._value = value

    @property
    def value(self) -> T | None:
        return self._value

    @value.setter
    def value(self, v: T | None) -> None:
        self._value = v

    def __str__(self) -> str:
        return f"AnyData({self._value})"


class ObservableFunction(Generic[Input, Output]):
    """A class that represents a pure function that can be observed by other classes.
    It stores the input and output of the function, as well as optional parameters
    It recomputes the output when the input is modified, or when the parameters are modified.

    It also stores the last exception message and traceback, if the function raised an exception.
    """

    _function: PureFunction
    _input: ObservableData[Input]
    _output: ObservableData[Output]

    _signature: inspect.Signature | None

    last_exception_message: Optional[str] = None
    last_exception_traceback: Optional[str] = None

    def __init__(self, f: Callable[[Input], Output]) -> None:
        self._function = f
        self._input = ObservableData()
        self._output = ObservableData()
        try:
            self._signature = inspect.signature(f)
        except ValueError:
            self._signature = None

    def name(self) -> str:
        return self._function.__name__

    def _compute_output(self) -> None:
        input_value = self._input.value
        try:
            r = self._function(input_value)
            self._output.value = r
            self.last_exception_message = None
            self.last_exception_traceback = None
        except Exception as e:
            self.last_exception_message = str(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.last_exception_traceback = "".join(traceback_details)
            self._output.value = None
        r = None

    def set_input_value(self, value: Any) -> None:
        self._input.value = value
        self._compute_output()

    def get_input(self) -> ObservableData[Input]:
        return self._input

    def get_output(self) -> ObservableData[Output]:
        return self._output

    def signature(self) -> inspect.Signature | None:
        return self._signature

    def nb_params(self) -> int | None:
        if self._signature is None:
            return None
        return len(self._signature.parameters)


def sandbox1() -> None:
    def f(a: int) -> int:
        return a + 3

    # obs_f = ObservableFunction(math.log)
    obs_f = ObservableFunction(f)
    obs_f.set_input_value(3)
    print(obs_f.get_input())
    print(obs_f.get_output())
    # print(obs_f.signature())
    # print(obs_f.nb_params())


if __name__ == "__main__":
    sandbox1()
