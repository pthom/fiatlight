from fiatlight import fiat_core, fiat_widgets, fiat_types, fiat_image, fiat_runner, fiat_config
from fiatlight.fiat_core import to_function_with_gui, AnyDataWithGui, FunctionWithGui, FunctionsGraph
from fiatlight.fiat_runner import fiat_run, FiatGuiParams, fiat_run_composition


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
    # from core
    "FunctionsGraph",
    "to_function_with_gui",
    "AnyDataWithGui",
    "FunctionWithGui",
    # from fiat_runner
    "fiat_run",
    "FiatGuiParams",
    "fiat_run_composition",
    # from here
    "demo_assets_dir",
]
