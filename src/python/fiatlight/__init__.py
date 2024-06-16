from fiatlight import fiat_core, fiat_widgets, fiat_types, fiat_runner, fiat_config, fiat_kits
from fiatlight.fiat_core import AnyDataWithGui, FunctionWithGui, FunctionsGraph, FiatToGuiException
from fiatlight.fiat_runner import (
    run,
    fiat_run,
    fiat_run_composition,
    fiat_run_graph,
    FiatGuiParams,
    fire_once_at_frame_end,
    fire_once_at_frame_start,
)
from fiatlight.fiat_kits import fiat_image, fiat_array
from fiatlight.fiat_widgets.fiat_osd import is_rendering_in_node, is_rendering_in_fiatlight_detached_window
from fiatlight.fiat_togui import (
    register_type,
    register_dataclass,
    dataclass_with_gui_registration,
    register_base_model,
    base_model_with_gui_registration,
)
from fiatlight.fiat_utils import with_fiat_attributes, add_fiat_attributes
from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_types import DataValidationResult, Error, Unspecified, InvalidValue, ErrorValue, UnspecifiedValue
from imgui_bundle import hello_imgui


ImGuiTheme_ = hello_imgui.ImGuiTheme_


def demo_assets_dir() -> str:
    import os

    this_dir = os.path.dirname(__file__)
    assets_dir = os.path.abspath(f"{this_dir}/../../fiatlight_assets")
    return assets_dir


def fiatlight_dir() -> str:
    import os

    this_dir = os.path.dirname(__file__)
    return this_dir


__all__ = [
    # sub packages
    "fiat_core",
    "fiat_types",
    "fiat_runner",
    "fiat_nodes",
    "fiat_widgets",
    "fiat_config",
    "fiat_array",
    "fiat_kits",
    # from core
    "FunctionsGraph",
    "AnyDataWithGui",
    "FunctionWithGui",
    "FiatToGuiException",
    # from to_gui
    "register_type",
    "register_dataclass",
    "dataclass_with_gui_registration",
    "register_base_model",
    "base_model_with_gui_registration",
    # from fiat_runner
    "run",
    "fiat_run",
    "fiat_run_composition",
    "fiat_run_graph",
    "FiatGuiParams",
    "fire_once_at_frame_end",
    "fire_once_at_frame_start",
    # from here
    "demo_assets_dir",
    "fiatlight_dir",
    # fiat_kits subpackages
    "fiat_image",
    "fiat_array",
    # from fiat_widgets
    "is_rendering_in_node",
    "is_rendering_in_fiatlight_detached_window",
    # from fiat_config
    "get_fiat_config",
    # from fiat_utils
    "with_fiat_attributes",
    "add_fiat_attributes",
    # from fiat_types
    "DataValidationResult",
    "Error",
    "Unspecified",
    "InvalidValue",
    "ErrorValue",
    "UnspecifiedValue",
    # from imgui_bundle
    "ImGuiTheme_",
]
