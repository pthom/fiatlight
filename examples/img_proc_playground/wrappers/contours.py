"""Contour wrappers for the image-processing playground."""
import cv2
import numpy as np

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import Contours, ImageU8

from examples.img_proc_playground.fiat_cv_enums import (
    ContourApproximation,
    RetrievalMode,
)


@fl.with_fiat_attributes(
    fiat_tags=["contours", "cv2.imgproc"],
)
def find_contours(
    image: ImageU8,
    mode: RetrievalMode = RetrievalMode.RETR_EXTERNAL,
    method: ContourApproximation = ContourApproximation.CHAIN_APPROX_SIMPLE,
) -> Contours:
    """Find contours in a binary image.

    **When to use:** After thresholding (or Canny + a fill step) to extract
    object outlines. The output is a list of contours that can be drawn,
    counted, filtered by area, or fed to shape-fitting nodes.

    **Parameters:**
    - `mode`: which contours to keep (outermost only, flat list, or hierarchical).
    - `method`: how aggressively to compress straight segments.

    **See also:** `draw_contours`, `threshold`, `adaptive_threshold`.

    **OpenCV docs:** [cv2.findContours](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0)
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    contours, _hierarchy = cv2.findContours(gray, mode.value, method.value)
    return Contours(list(contours))


@fl.with_fiat_attributes(
    color_r__range=(0, 255),
    color_g__range=(0, 255),
    color_b__range=(0, 255),
    thickness__range=(-1, 10),
    contour_idx__range=(-1, 100),
    fiat_tags=["contours", "cv2.imgproc"],
)
def draw_contours(
    image: ImageU8,
    contours: Contours,
    color_r: int = 0,
    color_g: int = 255,
    color_b: int = 0,
    thickness: int = 2,
    contour_idx: int = -1,
) -> ImageU8:
    """Draw contours over an image.

    **When to use:** Visualize the output of `find_contours` on top of the
    source (or any other) image.

    **Parameters:**
    - `color_r`, `color_g`, `color_b`: stroke color (RGB, 0-255 each).
    - `thickness`: stroke width in pixels. `-1` fills each contour.
    - `contour_idx`: index of the single contour to draw, or `-1` for all.

    **See also:** `find_contours`.

    **OpenCV docs:** [cv2.drawContours](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#ga746c0625f1781f1ffc9056259103edbc)
    """
    out = np.ascontiguousarray(image).copy()
    cv2.drawContours(out, contours, contour_idx, (color_r, color_g, color_b), thickness)
    return out  # type: ignore
