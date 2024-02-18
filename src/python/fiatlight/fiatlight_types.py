from typing import Callable, Any, Sequence, TypeAlias
from fiatlight.function_with_gui import FunctionWithGui

PureFunction: TypeAlias = Callable[..., Any]

PureFunctionOrFunctionWithGui: TypeAlias = PureFunction | FunctionWithGui | Any

MixedFunctionsGraph: TypeAlias = Sequence[PureFunctionOrFunctionWithGui]

FunctionsWithGuiGraph: TypeAlias = Sequence[FunctionWithGui]
