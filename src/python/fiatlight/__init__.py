from fiatlight import fiat_core, fiat_widgets, fiat_types
from fiatlight.fiat_core import FunctionsGraph, to_function_with_gui, AnyDataWithGui, FunctionWithGui
from fiatlight.fiat_runner import fiat_run, FiatGuiParams


def demo_assets_dir() -> str:
    import os

    this_dir = os.path.dirname(__file__)
    assets_dir = os.path.abspath(f"{this_dir}/../../fiatlight_assets")
    return assets_dir


__all__ = [
    # sub packages
    "fiat_core",
    "fiat_types",
    "app_runner",
    "node_gui",
    "utils",
    "fiat_widgets",
    # from core
    "FunctionsGraph",
    "to_function_with_gui",
    "AnyDataWithGui",
    "FunctionWithGui",
    # from fiat_runner
    "fiat_run",
    "FiatGuiParams",
    # from here
    "demo_assets_dir",
]

# from fiatlight.types import (
#     Function,
#     VoidFunction,
#     BoolFunction,
#     Unspecified,
#     UnspecifiedValue,
#     Error,
#     ErrorValue,
#     DataType,
#     FilePath,
#     ImagePath,
#     TextPath,
# )
# from fiatlight.core import (
#     AnyDataGuiCallbacks,
#     AnyDataWithGui,
#     ParamKind,
#     ParamWithGui,
#     OutputWithGui,
#     FunctionWithGui,
#     any_function_to_function_with_gui,
#     gui_factories,
#     FunctionNode,
#     FunctionNodeLink,
#     FunctionsGraph,
# )
# from fiatlight import core, fiat_runner, fiat_nodes, utils, widgets, types
# from fiatlight.fiat_runner import fiat_run, FiatGuiParams
#
#
#
#
# __all__ = [
#     # sub packages
#     "core",
#     "types",
#     "fiat_runner",
#     "fiat_nodes",
#     "utils",
#     "widgets",
#     # from fiatlight.types
#     "Function",
#     "VoidFunction",
#     "BoolFunction",
#     "Unspecified",
#     "UnspecifiedValue",
#     "Error",
#     "ErrorValue",
#     "DataType",
#     "FilePath",
#     "ImagePath",
#     "TextPath",
#     # from fiatlight.core
#     "AnyDataGuiCallbacks",
#     "AnyDataWithGui",
#     "ParamKind",
#     "ParamWithGui",
#     "OutputWithGui",
#     "FunctionWithGui",
#     "any_function_to_function_with_gui",
#     "gui_factories",
#     "FunctionNode",
#     "FunctionNodeLink",
#     "FunctionsGraph",
#     # from fiat_runner
#     "fiat_run",
#     "FiatGuiParams",
#     # from here
#     "demo_assets_dir",
# ]
