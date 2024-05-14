from . import fiat_image, fiat_array, fiat_ai
from .experimental import fiat_audio_simple
from .fiat_matplotlib import _register_figure_with_gui  # noqa

_register_figure_with_gui()


__all__ = ["fiat_image", "fiat_array", "fiat_audio_simple", "fiat_ai"]
