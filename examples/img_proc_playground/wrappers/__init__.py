"""Atomic wrappers for the image-processing playground.

`all_atomic_wrappers()` returns the full v0 palette in a stable order grouped
by intent. Each function carries a `_fiat_tags: List[str]` attribute used by
the playground's function palette to filter and group nodes.
"""
from typing import Callable, List

from examples.img_proc_playground.wrappers.source import image_source, imread_rgb
from examples.img_proc_playground.wrappers.color import color_convert
from examples.img_proc_playground.wrappers.filter import gaussian_blur, bilateral_filter
from examples.img_proc_playground.wrappers.edges import canny
from examples.img_proc_playground.wrappers.morphology import dilate, erode
from examples.img_proc_playground.wrappers.threshold import threshold, adaptive_threshold
from examples.img_proc_playground.wrappers.compositing import bitwise_and, bitwise_or
from examples.img_proc_playground.wrappers.geometry import resize


def all_atomic_wrappers() -> List[Callable]:
    """Return every atomic wrapper in v0, grouped by intent."""
    return [
        # source
        image_source,
        imread_rgb,
        # color
        color_convert,
        # filter
        gaussian_blur,
        bilateral_filter,
        # edges
        canny,
        # morphology
        dilate,
        erode,
        # threshold
        threshold,
        adaptive_threshold,
        # compositing
        bitwise_and,
        bitwise_or,
        # geometry
        resize,
    ]


__all__ = [
    "all_atomic_wrappers",
    "image_source",
    "imread_rgb",
    "color_convert",
    "gaussian_blur",
    "bilateral_filter",
    "canny",
    "dilate",
    "erode",
    "threshold",
    "adaptive_threshold",
    "bitwise_and",
    "bitwise_or",
    "resize",
]
