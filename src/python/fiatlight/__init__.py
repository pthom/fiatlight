from fiatlight import fiat_core, fiat_widgets, fiat_types, fiat_image, fiat_runner, fiat_config, fiat_array
from fiatlight.fiat_core import (
    AnyDataWithGui,
    FunctionWithGui,
    FunctionsGraph,
    register_type,
    register_enum,
    register_bound_int,
    register_bound_float,
)
from fiatlight.fiat_runner import fiat_run, fiat_run_composition, fiat_run_graph, FiatGuiParams


def demo_assets_dir() -> str:
    import os

    this_dir = os.path.dirname(__file__)
    assets_dir = os.path.abspath(f"{this_dir}/../../fiatlight_assets")
    return assets_dir


__all__ = [
    # sub packages
    "fiat_core",
    "fiat_types",
    "fiat_image",
    "fiat_runner",
    "fiat_nodes",
    "fiat_widgets",
    "fiat_config",
    "fiat_array",
    # from core
    "FunctionsGraph",
    "AnyDataWithGui",
    "FunctionWithGui",
    "register_type",
    "register_enum",
    "register_bound_int",
    "register_bound_float",
    # from fiat_runner
    "fiat_run",
    "fiat_run_composition",
    "fiat_run_graph",
    "FiatGuiParams",
    # from here
    "demo_assets_dir",
]
