"""Atomic wrappers for the image-processing playground.

`all_atomic_wrappers()` returns the full palette in a stable order grouped
by intent. Each function carries a `fiat_tags: List[str]` attribute used by
the playground's function palette to filter and group nodes.
"""
from typing import Callable, List

from examples.img_proc_playground.wrappers.source import image_source, imread_rgb
from examples.img_proc_playground.wrappers.color import color_convert
from examples.img_proc_playground.wrappers.tone import (
    applyColorMap,
    clahe,
    convertScaleAbs,
    equalizeHist,
)
from examples.img_proc_playground.wrappers.filter import (
    GaussianBlur,
    Laplacian,
    Scharr,
    Sobel,
    bilateralFilter,
    boxFilter,
    medianBlur,
)
from examples.img_proc_playground.wrappers.photo import (
    edgePreservingFilter,
    fastNlMeansDenoising,
    fastNlMeansDenoisingColored,
    stylization,
)
from examples.img_proc_playground.wrappers.edges import Canny
from examples.img_proc_playground.wrappers.morphology import dilate, erode, morphologyEx
from examples.img_proc_playground.wrappers.threshold import threshold, adaptiveThreshold
from examples.img_proc_playground.wrappers.compositing import (
    absdiff,
    addWeighted,
    bitwise_and,
    bitwise_not,
    bitwise_or,
    bitwise_xor,
)
from examples.img_proc_playground.wrappers.geometry import copyMakeBorder, flip, resize, rotate


def all_atomic_wrappers() -> List[Callable]:
    """Return every atomic wrapper, grouped by intent."""
    return [
        # source
        image_source,
        imread_rgb,
        # color / tone
        color_convert,
        equalizeHist,
        clahe,
        applyColorMap,
        convertScaleAbs,
        # filter
        GaussianBlur,
        bilateralFilter,
        medianBlur,
        boxFilter,
        Sobel,
        Scharr,
        Laplacian,
        # photo
        fastNlMeansDenoising,
        fastNlMeansDenoisingColored,
        stylization,
        edgePreservingFilter,
        # edges
        Canny,
        # morphology
        dilate,
        erode,
        morphologyEx,
        # threshold
        threshold,
        adaptiveThreshold,
        # compositing
        bitwise_and,
        bitwise_or,
        bitwise_xor,
        bitwise_not,
        addWeighted,
        absdiff,
        # geometry
        resize,
        flip,
        rotate,
        copyMakeBorder,
    ]


__all__ = [
    "all_atomic_wrappers",
    "image_source",
    "imread_rgb",
    "color_convert",
    "equalizeHist",
    "clahe",
    "applyColorMap",
    "convertScaleAbs",
    "GaussianBlur",
    "bilateralFilter",
    "medianBlur",
    "boxFilter",
    "Sobel",
    "Scharr",
    "Laplacian",
    "fastNlMeansDenoising",
    "fastNlMeansDenoisingColored",
    "stylization",
    "edgePreservingFilter",
    "Canny",
    "dilate",
    "erode",
    "morphologyEx",
    "threshold",
    "adaptiveThreshold",
    "bitwise_and",
    "bitwise_or",
    "bitwise_xor",
    "bitwise_not",
    "addWeighted",
    "absdiff",
    "resize",
    "flip",
    "rotate",
    "copyMakeBorder",
]
