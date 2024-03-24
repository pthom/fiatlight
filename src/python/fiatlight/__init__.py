from fiatlight import fiat_core, fiat_widgets, fiat_types, fiat_image, fiat_runner
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
    "fiat_image",
    "fiat_runner",
    "fiat_nodes",
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
