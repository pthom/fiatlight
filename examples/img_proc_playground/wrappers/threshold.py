"""Thresholding wrappers for the image-processing playground."""
from typing import NamedTuple

import numpy as np

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY

import cv2

from examples.img_proc_playground.fiat_cv_enums import (
    AdaptiveMethod,
    AdaptiveThresholdType,
    AutoThresholdMethod,
    DistanceMaskSize,
    DistanceType,
    ThresholdMode,
)


class ThresholdResult(NamedTuple):
    """Two-pin output of `threshold`: the resolved threshold value and the
    thresholded image.

    `used_thresh` equals the input `thresh` when `auto` is `NONE`, and the
    automatically-computed level when `auto` is `OTSU` or `TRIANGLE`.
    """

    used_thresh: float
    dst: ImageU8_GRAY


def _block_size_validator(blockSize: int) -> int:
    """Adaptive threshold requires an odd `blockSize` >= 3. Auto-correct
    to the nearest odd integer >= 3 — this is "obviously what the user meant"
    when they drag a slider through even values."""
    if blockSize < 3:
        blockSize = 3
    if blockSize % 2 == 0:
        blockSize += 1
    return blockSize


@fl.with_fiat_attributes(
    thresh__range=(0.0, 255.0),
    maxval__range=(0.0, 255.0),
    fiat_tags=["threshold", "cv2.imgproc"],
)
def threshold(
    image: ImageU8_GRAY,
    thresh: float = 128.0,
    maxval: float = 255.0,
    mode: ThresholdMode = ThresholdMode.THRESH_BINARY,
    auto: AutoThresholdMethod = AutoThresholdMethod.NONE,
) -> ThresholdResult:
    """Apply a fixed-level threshold to a grayscale image.

    **When to use:** Quick binary segmentation when the foreground / background
    split is roughly uniform across the image. Use `adaptiveThreshold` instead
    when lighting varies across the frame.

    **Parameters:**
    - `thresh`: threshold value. **Ignored** when `auto` is `OTSU` or `TRIANGLE`.
    - `maxval`: pixel value assigned to "above threshold" in BINARY-style modes.
    - `mode`: comparison rule (BINARY, BINARY_INV, TRUNC, TOZERO, TOZERO_INV).
    - `auto`: optional automatic threshold-value computation (NONE / OTSU /
      TRIANGLE). Both auto methods require a single-channel 8-bit image.

    **Outputs:**
    - `used_thresh`: the threshold value cv2 actually applied (= `thresh` unless
      OTSU / TRIANGLE picked one for you).
    - `dst`: the thresholded image.

    **See also:** `adaptiveThreshold` (per-pixel threshold), `Canny`.

    **OpenCV docs:** [cv2.threshold](https://docs.opencv.org/4.13.0/d7/d1b/group__imgproc__misc.html#gae8a4a146d1ca78c626a53577199e9c57)
    """
    flag = mode.value
    if auto is not AutoThresholdMethod.NONE:
        flag |= auto.value
    used_thresh, r = cv2.threshold(image, thresh, maxval, flag)
    return ThresholdResult(float(used_thresh), r)


@fl.with_fiat_attributes(
    maxValue__range=(0.0, 255.0),
    blockSize__range=(3, 51),
    blockSize__validator=_block_size_validator,
    C__range=(-50.0, 50.0),
    fiat_tags=["threshold", "cv2.imgproc"],
)
def adaptiveThreshold(
    image: ImageU8_GRAY,
    maxValue: float = 255.0,
    adaptiveMethod: AdaptiveMethod = AdaptiveMethod.ADAPTIVE_THRESH_GAUSSIAN_C,
    thresholdType: AdaptiveThresholdType = AdaptiveThresholdType.THRESH_BINARY,
    blockSize: int = 11,
    C: float = 2.0,
) -> ImageU8_GRAY:
    """Per-pixel threshold whose level depends on a local neighbourhood.

    **When to use:** When lighting varies across the image (shadows, gradients).
    Robust where a single global threshold fails.

    **Parameters:**
    - `maxValue`: value assigned to pixels above the local threshold.
    - `adaptiveMethod`: how the local threshold is computed (mean or Gaussian-weighted).
    - `thresholdType`: BINARY or BINARY_INV; other modes are not supported by cv2.
    - `blockSize`: side of the local neighbourhood. Must be odd, >= 3.
    - `C`: constant subtracted from the local mean. Higher = stricter.

    **See also:** `threshold` (global threshold), `GaussianBlur`.

    **OpenCV docs:** [cv2.adaptiveThreshold](https://docs.opencv.org/4.13.0/d7/d1b/group__imgproc__misc.html#ga72b913f352e4a1b1b397736707afcde3)
    """
    r = cv2.adaptiveThreshold(image, maxValue, adaptiveMethod.value, thresholdType.value, blockSize, C)
    return r  # type: ignore


@fl.with_fiat_attributes(
    lowerb_0__range=(0, 255),
    lowerb_1__range=(0, 255),
    lowerb_2__range=(0, 255),
    upperb_0__range=(0, 255),
    upperb_1__range=(0, 255),
    upperb_2__range=(0, 255),
    fiat_tags=["threshold", "color", "cv2.core"],
)
def inRange(
    image: ImageU8,
    lowerb_0: int = 0,
    lowerb_1: int = 0,
    lowerb_2: int = 0,
    upperb_0: int = 255,
    upperb_1: int = 255,
    upperb_2: int = 255,
) -> ImageU8_GRAY:
    """Per-pixel test that all channel values fall within a `[lowerb, upperb]` range.

    **When to use:** Color masking — typically on an HSV image to isolate a hue
    range. Output is a binary mask (255 inside, 0 outside).

    **Parameters:**
    - `lowerb_0/1/2`: lower bound for channel 0 / 1 / 2.
    - `upperb_0/1/2`: upper bound for channel 0 / 1 / 2.

    For grayscale input only `lowerb_0` / `upperb_0` are used.

    **See also:** `threshold`, `bitwise_and` (combine masks).

    **OpenCV docs:** [cv2.inRange](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga48af0ab51e36436c5d04340e036ce981)
    """
    if image.ndim == 2:
        lower: tuple[int, ...] = (lowerb_0,)
        upper: tuple[int, ...] = (upperb_0,)
    else:
        lower = (lowerb_0, lowerb_1, lowerb_2)
        upper = (upperb_0, upperb_1, upperb_2)
    r = cv2.inRange(image, lower, upper)
    return r  # type: ignore


@fl.with_fiat_attributes(fiat_tags=["threshold", "cv2.imgproc"])
def distanceTransform(
    image: ImageU8_GRAY,
    distanceType: DistanceType = DistanceType.DIST_L2,
    maskSize: DistanceMaskSize = DistanceMaskSize.MASK_3,
) -> ImageU8_GRAY:
    """For each non-zero pixel, the distance to the nearest zero pixel.

    **When to use:** Refine a binary mask — for example to find the thickest
    parts of a foreground region (peaks of the distance map mark
    "centers" of blobs), or to seed `cv2.watershed`.

    The cv2 output is float; this wrapper normalises to U8 for display. For
    numerical work, call `cv2.distanceTransform` directly.

    **Parameters:**
    - `distanceType`: metric (L1, L2 = Euclidean, Chebyshev).
    - `maskSize`: 3, 5, or `MASK_PRECISE` (only valid with L2).

    **See also:** `threshold`, `morphologyEx` (skeletonization).

    **OpenCV docs:** [cv2.distanceTransform](https://docs.opencv.org/4.13.0/d7/d1b/group__imgproc__misc.html#ga8a0b7fdfcb7a13dde018988ba3a43042)
    """
    dist = cv2.distanceTransform(image, distanceType.value, maskSize.value)
    r = cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return r  # type: ignore
