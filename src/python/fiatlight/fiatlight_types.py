from typing import Callable, Any, Sequence, TypeAlias
from fiatlight.function_with_gui import FunctionWithGui

PureFunction: TypeAlias = Callable[[Any], Any]

PureFunctionOrFunctionWithGui: TypeAlias = PureFunction | FunctionWithGui

MixedFunctionsGraph: TypeAlias = Sequence[PureFunctionOrFunctionWithGui]

FunctionsWithGuiGraph: TypeAlias = Sequence[FunctionWithGui]
