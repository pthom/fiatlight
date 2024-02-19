from fiatlight.f2.parameter_with_gui import ParameterWithGui

from typing import Any, List, TypeVar, Generic, Union, TypeAlias, Callable
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
    def name(self) -> str:
        pass

    def __call__(self, x: Input) -> Output:
        return self.f(x)


PureFunctionOrFunctionWithWrappedParams: TypeAlias = Union[
    Callable[[Input], Output], FunctionWithSettableParams[Input, Output]
]


__all__ = ["FunctionWithSettableParams", "PureFunctionOrFunctionWithWrappedParams", "ParameterWithGui"]
