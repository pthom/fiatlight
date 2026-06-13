"""Histogram wrappers for the image-processing playground.

Outputs use `FloatMatrix_Dim1` / `FloatMatrix_Dim2` from `fiat_implot`,
which already have plot-style GUIs registered — so a histogram pin
renders as a curve / heatmap with no extra glue.
"""
import cv2
import numpy as np

from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY
from fiatlight.fiat_kits.fiat_implot import FloatMatrix_Dim1, FloatMatrix_Dim2


@with_fiat_attributes(
    channel__range=(0, 3),
    bins__range=(8, 512),
    range_min__range=(0.0, 255.0),
    range_max__range=(0.0, 255.0),
    fiat_tags=["histogram"],
)
def calcHist1D(
    image: ImageU8,
    channel: int = 0,
    bins: int = 64,
    range_min: float = 0.0,
    range_max: float = 256.0,
) -> FloatMatrix_Dim1:
    """1-D histogram of one channel of an image.

    **When to use:** Inspect intensity / color distribution. Output is
    a 1-D float array — the `fiat_implot` plot widget renders it as a
    curve.

    **Parameters:**
    - `channel`: channel index to histogram (0 = first channel).
    - `bins`: number of histogram bins.
    - `range_min`, `range_max`: value range covered (cv2 expects the upper
      bound *exclusive*; for U8 use `[0, 256]`).

    **See also:** `equalizeHist`, `clahe`, `calcBackProject`.

    **OpenCV docs:** [cv2.calcHist](https://docs.opencv.org/4.13.0/d6/dc7/group__imgproc__hist.html#ga4b2b5fd75503ff9e6844cc4dcdaed35d)
    """
    arr = cv2.calcHist([image], [channel], None, [bins], [range_min, range_max])
    return FloatMatrix_Dim1(arr.reshape(-1).astype(np.float32))


@with_fiat_attributes(
    channel0__range=(0, 3),
    channel1__range=(0, 3),
    bins0__range=(8, 256),
    bins1__range=(8, 256),
    fiat_tags=["histogram"],
)
def calcHist2D(
    image: ImageU8,
    channel0: int = 0,
    channel1: int = 1,
    bins0: int = 32,
    bins1: int = 32,
) -> FloatMatrix_Dim2:
    """2-D joint histogram of two channels.

    **When to use:** Visualize the joint distribution of two channels,
    e.g. (Hue, Saturation) on an HSV image. Output is a 2-D float array
    rendered as a heatmap by the `fiat_implot` plot widget.

    Range is fixed to `[0, 256)` per channel (the U8 default).

    **OpenCV docs:** [cv2.calcHist](https://docs.opencv.org/4.13.0/d6/dc7/group__imgproc__hist.html#ga4b2b5fd75503ff9e6844cc4dcdaed35d)
    """
    arr = cv2.calcHist([image], [channel0, channel1], None, [bins0, bins1], [0.0, 256.0, 0.0, 256.0])
    return FloatMatrix_Dim2(arr.astype(np.float32))


@with_fiat_attributes(
    channel__range=(0, 3),
    range_min__range=(0.0, 255.0),
    range_max__range=(0.0, 255.0),
    scale__range=(0.1, 100.0),
    scale__slider_logarithmic=True,
    fiat_tags=["histogram"],
)
def calcBackProject(
    image: ImageU8,
    hist: FloatMatrix_Dim1,
    channel: int = 0,
    range_min: float = 0.0,
    range_max: float = 256.0,
    scale: float = 1.0,
) -> ImageU8_GRAY:
    """Back-project a 1-D histogram onto an image.

    **When to use:** Highlight regions whose pixel distribution matches a
    reference histogram (typical use: object localisation by colour).
    Pair with `calcHist1D` on a region of interest, then back-project on
    the full image.

    **Parameters:**
    - `channel`: channel of `image` to look up in the histogram.
    - `range_min`, `range_max`: same range used when computing the histogram.
    - `scale`: multiplied into the output before clipping to U8.

    **OpenCV docs:** [cv2.calcBackProject](https://docs.opencv.org/4.13.0/d6/dc7/group__imgproc__hist.html#ga3a0af640716b456c3d14af8aee12e3ca)
    """
    h = hist.reshape(-1, 1).astype(np.float32)
    r = cv2.calcBackProject([image], [channel], h, [range_min, range_max], scale)
    return r  # type: ignore
