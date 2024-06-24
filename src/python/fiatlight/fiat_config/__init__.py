from .fiat_config_def import (
    FiatConfig,
    FiatRunConfig,
)
from .fiat_style_def import FiatColorType, FiatStyle
from .load_save_default_run_config import get_fiat_config


def fiatlight_python_src_path() -> str:
    import os

    this_dir = os.path.dirname(os.path.abspath(__file__))
    r = os.path.abspath(os.path.join(this_dir, ".."))
    return r


def fiatlight_doc_path() -> str:
    r = f"{fiatlight_python_src_path()}/doc"
    return r


__all__ = [
    # from fiat_config_def.py
    "get_fiat_config",
    "FiatConfig",
    "FiatRunConfig",
    # from here
    "fiatlight_python_src_path",
    "fiatlight_doc_path",
    # to here
    "FiatColorType",
    "FiatStyle",
]
