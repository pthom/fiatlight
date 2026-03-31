from . import fiat_image, fiat_implot, fiat_ai

__all__ = ["fiat_image", "fiat_implot", "fiat_ai"]

import importlib.util

if importlib.util.find_spec("pandas") is not None:
    __all__.append("fiat_dataframe")

if importlib.util.find_spec("matplotlib") is not None:
    __all__.append("fiat_matplotlib")
    # from .experimental import fiat_audio_simple
    from .fiat_matplotlib import _register_figure_with_gui  # noqa

    _register_figure_with_gui()
