from fiatlight.fiat_config.fiat_config_def import (
    FiatConfig,
    get_fiat_config,
    FiatStyle,
    FiatColorType,
)


def fiatlight_python_src_path() -> str:
    import os

    this_dir = os.path.dirname(os.path.abspath(__file__))
    r = os.path.abspath(os.path.join(this_dir, ".."))
    return r


def fiatlight_doc_path() -> str:
    r = f"{fiatlight_python_src_path()}/doc"
    return r


__all__ = [
    "get_fiat_config",
    "FiatConfig",
    "FiatColorType",
    "FiatStyle",
    # from here
    "fiatlight_python_src_path",
    "fiatlight_doc_path",
]
