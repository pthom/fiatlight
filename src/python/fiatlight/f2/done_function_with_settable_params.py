from fiatlight.f2.parameter_with_gui import ParameterWithGui

from typing import Any, List, TypeVar, Generic
from abc import ABC, abstractmethod


Input = TypeVar("Input")
Output = TypeVar("Output")


class FunctionWithSettableParams(ABC, Generic[Input, Output]):
    """An abstract class that represents a function with settable parameters."""

    parameters_with_gui: List[ParameterWithGui[Any]]  # fill this at construction, with the parameters and their gui

    @abstractmethod
    def f(self, value: Input) -> Output:
        """override this with the actual function implementation"""
        pass

    @abstractmethod
    def present_output(self, value: Output) -> None:
        """override this with the actual function output presentation"""
        pass

    def __call__(self, x: Input) -> Output:
        return self.f(x)


__all__ = ["FunctionWithSettableParams", "ParameterWithGui"]
