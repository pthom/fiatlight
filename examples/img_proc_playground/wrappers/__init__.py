"""Atomic wrappers for the image-processing playground.

`all_atomic_wrappers()` returns the full palette in a stable order grouped
by intent. Each function carries a `fiat_tags: List[str]` attribute used by
the playground's function palette to filter and group nodes.
"""
from typing import Callable, List

from examples.img_proc_playground.wrappers.source import image_source, imread_rgb
from examples.img_proc_playground.wrappers.color import color_convert
from examples.img_proc_playground.wrappers.tone import (
    apply_color_map,
    clahe,
    convert_scale_abs,
    equalize_hist,
)
from examples.img_proc_playground.wrappers.filter import (
    bilateral_filter,
    box_filter,
    gaussian_blur,
    laplacian,
    median_blur,
    scharr,
    sobel,
)
from examples.img_proc_playground.wrappers.photo import (
    edge_preserving_filter,
    fast_nl_means_denoising,
    fast_nl_means_denoising_colored,
    stylization,
)
from examples.img_proc_playground.wrappers.edges import canny
from examples.img_proc_playground.wrappers.morphology import dilate, erode, morphology_ex
from examples.img_proc_playground.wrappers.threshold import threshold, adaptive_threshold
from examples.img_proc_playground.wrappers.compositing import (
    absdiff,
    add_weighted,
    bitwise_and,
    bitwise_not,
    bitwise_or,
    bitwise_xor,
)
from examples.img_proc_playground.wrappers.geometry import copy_make_border, flip, resize, rotate


def all_atomic_wrappers() -> List[Callable]:
    """Return every atomic wrapper, grouped by intent."""
    return [
        # source
        image_source,
        imread_rgb,
        # color / tone
        color_convert,
        equalize_hist,
        clahe,
        apply_color_map,
        convert_scale_abs,
        # filter
        gaussian_blur,
        bilateral_filter,
        median_blur,
        box_filter,
        sobel,
        scharr,
        laplacian,
        # photo
        fast_nl_means_denoising,
        fast_nl_means_denoising_colored,
        stylization,
        edge_preserving_filter,
        # edges
        canny,
        # morphology
        dilate,
        erode,
        morphology_ex,
        # threshold
        threshold,
        adaptive_threshold,
        # compositing
        bitwise_and,
        bitwise_or,
        bitwise_xor,
        bitwise_not,
        add_weighted,
        absdiff,
        # geometry
        resize,
        flip,
        rotate,
        copy_make_border,
    ]


__all__ = [
    "all_atomic_wrappers",
    "image_source",
    "imread_rgb",
    "color_convert",
    "equalize_hist",
    "clahe",
    "apply_color_map",
    "convert_scale_abs",
    "gaussian_blur",
    "bilateral_filter",
    "median_blur",
    "box_filter",
    "sobel",
    "scharr",
    "laplacian",
    "fast_nl_means_denoising",
    "fast_nl_means_denoising_colored",
    "stylization",
    "edge_preserving_filter",
    "canny",
    "dilate",
    "erode",
    "morphology_ex",
    "threshold",
    "adaptive_threshold",
    "bitwise_and",
    "bitwise_or",
    "bitwise_xor",
    "bitwise_not",
    "add_weighted",
    "absdiff",
    "resize",
    "flip",
    "rotate",
    "copy_make_border",
]
