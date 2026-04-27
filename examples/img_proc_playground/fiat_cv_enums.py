"""Shared OpenCV enums used by the playground wrappers.

Wrappers replace cv2's flag-style int parameters with Python `Enum`s so the
fiatlight GUI shows a dropdown of named, valid choices instead of a free-int
slider that hides which values cv2 accepts.

Add new enums here when a new wrapper needs one — keep them ordered roughly
by the cv2 module they belong to.
"""
from enum import Enum

import cv2


class CannyApertureSize(Enum):
    """Aperture size of the Sobel filter inside `cv2.Canny`."""

    APERTURE_3 = 3
    APERTURE_5 = 5
    APERTURE_7 = 7


class GaussianKsize(Enum):
    """Common odd kernel sizes for `cv2.GaussianBlur`.

    cv2 also accepts `(0, 0)` to compute the kernel from sigma, but for the
    playground we expose explicit odd values to keep the slider semantics clear.
    """

    K_3 = 3
    K_5 = 5
    K_7 = 7
    K_9 = 9
    K_11 = 11


class BorderType(Enum):
    """Border extrapolation mode for filters that read outside the image."""

    BORDER_DEFAULT = cv2.BORDER_DEFAULT
    BORDER_REPLICATE = cv2.BORDER_REPLICATE
    BORDER_REFLECT = cv2.BORDER_REFLECT
    BORDER_REFLECT_101 = cv2.BORDER_REFLECT_101
    BORDER_WRAP = cv2.BORDER_WRAP
    BORDER_ISOLATED = cv2.BORDER_ISOLATED


class MorphShape(Enum):
    """Structuring-element shape for morphological operations."""

    MORPH_RECT = cv2.MORPH_RECT
    MORPH_CROSS = cv2.MORPH_CROSS
    MORPH_ELLIPSE = cv2.MORPH_ELLIPSE


class ThresholdMode(Enum):
    """Comparison rule for `cv2.threshold` — what to do with each pixel.

    Orthogonal to `AutoThresholdMethod`: pick a comparison rule here, then
    optionally pick an auto-threshold method.
    """

    THRESH_BINARY = cv2.THRESH_BINARY
    THRESH_BINARY_INV = cv2.THRESH_BINARY_INV
    THRESH_TRUNC = cv2.THRESH_TRUNC
    THRESH_TOZERO = cv2.THRESH_TOZERO
    THRESH_TOZERO_INV = cv2.THRESH_TOZERO_INV


class AutoThresholdMethod(Enum):
    """Automatic threshold-value computation for `cv2.threshold`.

    When set to anything other than `NONE`, the `thresh` parameter passed
    to `cv2.threshold` is ignored — cv2 picks the threshold itself.
    Both methods require a single-channel 8-bit image.
    """

    NONE = 0
    OTSU = cv2.THRESH_OTSU
    TRIANGLE = cv2.THRESH_TRIANGLE


class AdaptiveThresholdType(Enum):
    """Thresholding mode accepted by `cv2.adaptiveThreshold` (binary only)."""

    THRESH_BINARY = cv2.THRESH_BINARY
    THRESH_BINARY_INV = cv2.THRESH_BINARY_INV


class AdaptiveMethod(Enum):
    """Local-mean computation method for `cv2.adaptiveThreshold`."""

    ADAPTIVE_THRESH_MEAN_C = cv2.ADAPTIVE_THRESH_MEAN_C
    ADAPTIVE_THRESH_GAUSSIAN_C = cv2.ADAPTIVE_THRESH_GAUSSIAN_C


class InterpolationFlag(Enum):
    """Interpolation mode for `cv2.resize` and other geometric transforms."""

    INTER_NEAREST = cv2.INTER_NEAREST
    INTER_LINEAR = cv2.INTER_LINEAR
    INTER_CUBIC = cv2.INTER_CUBIC
    INTER_AREA = cv2.INTER_AREA
    INTER_LANCZOS4 = cv2.INTER_LANCZOS4
