from fiatlux.any_data_with_gui import AnyDataWithGui
from fiatlux.function_with_gui import FunctionWithGui
from fiatlux.functions_composition_graph import FunctionsCompositionGraph

from fiatlux.base_data_with_gui import IntWithGui
from typing import Any, Callable


PureFunction = Callable[[Any], Any]


__all__ = [
    "PureFunction",
    "AnyDataWithGui",
    "FunctionWithGui",
    "FunctionsCompositionGraph",
    "IntWithGui",
]
