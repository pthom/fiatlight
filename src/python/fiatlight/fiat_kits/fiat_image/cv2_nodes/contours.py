"""Contour wrappers for the image-processing playground."""
from typing import NamedTuple

import cv2
import numpy as np

from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_kits.fiat_image import Contours, ContoursHierarchy, ImageU8
from fiatlight.fiat_types import ColorRgb

from .cv_enums import (
    ContourApproximation,
    RetrievalMode,
)


class FindContoursResult(NamedTuple):
    """Two-pin output of `findContours`: the contour list and its hierarchy.

    NamedTuple → fiatlight splits this into two output pins, both
    typed and labelled, so a downstream `drawContours` can consume both.
    """

    contours: Contours
    hierarchy: ContoursHierarchy


@with_fiat_attributes(
    fiat_tags=["contours", "cv2.imgproc"],
)
def findContours(
    image: ImageU8,
    mode: RetrievalMode = RetrievalMode.RETR_EXTERNAL,
    method: ContourApproximation = ContourApproximation.CHAIN_APPROX_SIMPLE,
) -> FindContoursResult:
    """Find contours in a binary image.

    **When to use:** After thresholding (or Canny + a fill step) to extract
    object outlines. Outputs both the contour list and the hierarchy array,
    so a downstream `drawContours` can filter by tree depth via `maxLevel`.

    **Parameters:**
    - `mode`: which contours to keep (outermost only, flat list, or hierarchical).
    - `method`: how aggressively to compress straight segments.

    **See also:** `drawContours`, `threshold`, `adaptiveThreshold`.

    **OpenCV docs:** [cv2.findContours](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0)
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    contours, hierarchy = cv2.findContours(gray, mode.value, method.value)
    if hierarchy is None:
        hierarchy = np.empty((1, 0, 4), dtype=np.int32)
    return FindContoursResult(Contours(list(contours)), ContoursHierarchy(hierarchy))


@with_fiat_attributes(
    thickness__range=(-1, 10),
    contourIdx__range=(-1, 100),
    maxLevel__range=(0, 10),
    fiat_tags=["contours", "cv2.imgproc"],
)
def drawContours(
    image: ImageU8,
    contours: Contours,
    hierarchy: ContoursHierarchy | None = None,
    color: ColorRgb = ColorRgb((0, 255, 0)),
    thickness: int = 2,
    contourIdx: int = -1,
    maxLevel: int = 0,
) -> ImageU8:
    """Draw contours over an image, optionally filtered by tree depth.

    **When to use:** Visualize the output of `findContours` on top of the
    source (or any other) image. With a hierarchy wired in, `maxLevel`
    restricts which depths get drawn (0 = outer only, 1 = outer + immediate
    holes, …). Ignored when `contourIdx >= 0`.

    **Parameters:**
    - `color`: stroke color (RGB).
    - `thickness`: stroke width in pixels. `-1` fills each contour.
    - `contourIdx`: index of a single contour to draw, or `-1` for all.
    - `maxLevel`: tree-depth cutoff (only used when drawing all contours).

    **See also:** `findContours`.

    **OpenCV docs:** [cv2.drawContours](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#ga746c0625f1781f1ffc9056259103edbc)
    """
    out = np.ascontiguousarray(image).copy()
    cv2.drawContours(
        out,
        contours,
        contourIdx,
        tuple(color),
        thickness,
        cv2.LINE_8,
        hierarchy,
        maxLevel,
    )
    return out  # type: ignore
