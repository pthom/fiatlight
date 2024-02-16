from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import FunctionWithGui
from fiatlight.functions_composition_graph import FunctionsCompositionGraph

from fiatlight.base_data_with_gui import IntWithGui
from typing import Any, Callable


PureFunction = Callable[[Any], Any]


__all__ = [
    "PureFunction",
    "AnyDataWithGui",
    "FunctionWithGui",
    "FunctionsCompositionGraph",
    "IntWithGui",
]
