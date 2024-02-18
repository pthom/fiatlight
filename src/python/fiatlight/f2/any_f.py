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
    Note: _value can be a tuple
          As it is used to store input and output of functions, it will be a tuple
          in the case of a function with multiple parameters,
          or a function that returns multiple values
    """

    _value: T | None

    def __init__(self, secret_key: str) -> None:
        if secret_key != "fiatlight":
            raise ValueError("This class should not be instantiated directly. Use the factory methods instead.")
        pass

    @staticmethod
    def create_none() -> "ObservableData[T]":
        d = ObservableData[T]("fiatlight")
        d.value = None
        return d

    @staticmethod
    def create_with_value(value: Any) -> "ObservableData[T]":
        d = ObservableData[T]("fiatlight")
        d.value = value
        return d

    @property
    def value(self) -> T | None:
        return self._value

    @value.setter
    def value(self, v: T | None) -> None:
        self._value = v

    def is_none(self) -> bool:
        """Returns True if a value was stored in this object, and it is None."""
        return self._value is None

    def is_tuple(self) -> bool:
        """Returns True if the value is a tuple."""
        return isinstance(self._value, tuple)

    def nb_values(self) -> int:
        """Returns the number of values stored in this object, if it is a tuple."""
        if self.is_tuple():
            assert isinstance(self._value, tuple)
            return len(self._value)
        else:
            return 1

    def get_value_at(self, index: int) -> Any:
        assert isinstance(self._value, tuple)
        assert 0 <= index < len(self._value)
        return self._value[index]

    def set_value_at(self, index: int, value: Any) -> None:
        assert self.is_tuple()
        assert isinstance(self._value, tuple)
        new_value = self._value[:index] + (value,) + self._value[index + 1 :]
        self.value = new_value  # type: ignore

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
        self._input = ObservableData.create_none()
        self._output = ObservableData.create_none()
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
