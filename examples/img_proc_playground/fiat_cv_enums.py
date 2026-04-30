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
    BORDER_CONSTANT = cv2.BORDER_CONSTANT
    BORDER_ISOLATED = cv2.BORDER_ISOLATED


class MorphShape(Enum):
    """Structuring-element shape for morphological operations."""

    MORPH_RECT = cv2.MORPH_RECT
    MORPH_CROSS = cv2.MORPH_CROSS
    MORPH_ELLIPSE = cv2.MORPH_ELLIPSE


class MorphOp(Enum):
    """Composite morphological operations exposed by `cv2.morphologyEx`.

    Erode / dilate are exposed as their own wrappers — this enum only lists
    the higher-level combinations.
    """

    MORPH_OPEN = cv2.MORPH_OPEN
    MORPH_CLOSE = cv2.MORPH_CLOSE
    MORPH_GRADIENT = cv2.MORPH_GRADIENT
    MORPH_TOPHAT = cv2.MORPH_TOPHAT
    MORPH_BLACKHAT = cv2.MORPH_BLACKHAT


class FlipCode(Enum):
    """Axis around which `cv2.flip` flips the image.

    cv2 uses an int flag: 0 = around X axis (vertical flip), 1 = around Y
    axis (horizontal flip), -1 = around both (180° rotation).
    """

    VERTICAL = 0
    HORIZONTAL = 1
    BOTH = -1


class RotateCode(Enum):
    """Quarter-turn rotation passed to `cv2.rotate`."""

    ROTATE_90_CW = cv2.ROTATE_90_CLOCKWISE
    ROTATE_180 = cv2.ROTATE_180
    ROTATE_90_CCW = cv2.ROTATE_90_COUNTERCLOCKWISE


class SobelKsize(Enum):
    """Aperture sizes accepted by `cv2.Sobel` / `cv2.Laplacian`.

    `K_1` is a special case: cv2 uses a 1×3 / 3×1 Scharr-like kernel.
    """

    K_1 = 1
    K_3 = 3
    K_5 = 5
    K_7 = 7


class ColorMap(Enum):
    """Built-in cv2 color maps for `cv2.applyColorMap`.

    Maps a single-channel image to a 3-channel BGR image.
    """

    AUTUMN = cv2.COLORMAP_AUTUMN
    BONE = cv2.COLORMAP_BONE
    JET = cv2.COLORMAP_JET
    WINTER = cv2.COLORMAP_WINTER
    RAINBOW = cv2.COLORMAP_RAINBOW
    OCEAN = cv2.COLORMAP_OCEAN
    SUMMER = cv2.COLORMAP_SUMMER
    SPRING = cv2.COLORMAP_SPRING
    COOL = cv2.COLORMAP_COOL
    HSV = cv2.COLORMAP_HSV
    PINK = cv2.COLORMAP_PINK
    HOT = cv2.COLORMAP_HOT
    PARULA = cv2.COLORMAP_PARULA
    MAGMA = cv2.COLORMAP_MAGMA
    INFERNO = cv2.COLORMAP_INFERNO
    PLASMA = cv2.COLORMAP_PLASMA
    VIRIDIS = cv2.COLORMAP_VIRIDIS
    CIVIDIS = cv2.COLORMAP_CIVIDIS
    TWILIGHT = cv2.COLORMAP_TWILIGHT
    TWILIGHT_SHIFTED = cv2.COLORMAP_TWILIGHT_SHIFTED
    TURBO = cv2.COLORMAP_TURBO
    DEEPGREEN = cv2.COLORMAP_DEEPGREEN


class EdgePreservingFlag(Enum):
    """Algorithm variant for `cv2.edgePreservingFilter`."""

    RECURS_FILTER = cv2.RECURS_FILTER
    NORMCONV_FILTER = cv2.NORMCONV_FILTER


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


class DistanceType(Enum):
    """Distance metric used by `cv2.distanceTransform`."""

    DIST_L1 = cv2.DIST_L1
    DIST_L2 = cv2.DIST_L2
    DIST_C = cv2.DIST_C


class DistanceMaskSize(Enum):
    """Mask size for `cv2.distanceTransform` (3 / 5 / DIST_MASK_PRECISE)."""

    MASK_3 = cv2.DIST_MASK_3
    MASK_5 = cv2.DIST_MASK_5
    MASK_PRECISE = cv2.DIST_MASK_PRECISE


class RetrievalMode(Enum):
    """Contour retrieval mode for `cv2.findContours`.

    Controls which contours are returned and how they relate to one another:
    - **EXTERNAL**: only the outermost contours.
    - **LIST**: all contours, no parent/child relationship.
    - **CCOMP**: two-level hierarchy (outer + holes).
    - **TREE**: full nested hierarchy.
    """

    RETR_EXTERNAL = cv2.RETR_EXTERNAL
    RETR_LIST = cv2.RETR_LIST
    RETR_CCOMP = cv2.RETR_CCOMP
    RETR_TREE = cv2.RETR_TREE


class ContourApproximation(Enum):
    """Contour point compression for `cv2.findContours`.

    - **NONE**: keep every boundary pixel.
    - **SIMPLE**: collapse straight horizontal/vertical/diagonal segments to endpoints.
    - **TC89_L1** / **TC89_KCOS**: Teh-Chin approximation variants.
    """

    CHAIN_APPROX_NONE = cv2.CHAIN_APPROX_NONE
    CHAIN_APPROX_SIMPLE = cv2.CHAIN_APPROX_SIMPLE
    CHAIN_APPROX_TC89_L1 = cv2.CHAIN_APPROX_TC89_L1
    CHAIN_APPROX_TC89_KCOS = cv2.CHAIN_APPROX_TC89_KCOS
