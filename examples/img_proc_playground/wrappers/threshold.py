"""Thresholding wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8_GRAY

import cv2

from examples.img_proc_playground.fiat_cv_enums import (
    AdaptiveMethod,
    AdaptiveThresholdType,
    AutoThresholdMethod,
    ThresholdMode,
)


def _block_size_validator(block_size: int) -> int:
    """Adaptive threshold requires an odd `block_size` >= 3. Auto-correct
    to the nearest odd integer >= 3 — this is "obviously what the user meant"
    when they drag a slider through even values."""
    if block_size < 3:
        block_size = 3
    if block_size % 2 == 0:
        block_size += 1
    return block_size


@fl.with_fiat_attributes(
    thresh__range=(0.0, 255.0),
    maxval__range=(0.0, 255.0),
)
def threshold(
    image: ImageU8_GRAY,
    thresh: float = 128.0,
    maxval: float = 255.0,
    mode: ThresholdMode = ThresholdMode.THRESH_BINARY,
    auto: AutoThresholdMethod = AutoThresholdMethod.NONE,
) -> ImageU8_GRAY:
    """Apply a fixed-level threshold to a grayscale image.

    **When to use:** Quick binary segmentation when the foreground / background
    split is roughly uniform across the image. Use `adaptive_threshold` instead
    when lighting varies across the frame.

    **Parameters:**
    - `thresh`: threshold value. **Ignored** when `auto` is `OTSU` or `TRIANGLE`.
    - `maxval`: pixel value assigned to "above threshold" in BINARY-style modes.
    - `mode`: comparison rule (BINARY, BINARY_INV, TRUNC, TOZERO, TOZERO_INV).
    - `auto`: optional automatic threshold-value computation (NONE / OTSU /
      TRIANGLE). Both auto methods require a single-channel 8-bit image.

    **See also:** `adaptive_threshold` (per-pixel threshold), `canny`.

    **OpenCV docs:** [cv2.threshold](https://docs.opencv.org/4.13.0/d7/d1b/group__imgproc__misc.html#gae8a4a146d1ca78c626a53577199e9c57)
    """
    flag = mode.value
    if auto is not AutoThresholdMethod.NONE:
        flag |= auto.value
    _, r = cv2.threshold(image, thresh, maxval, flag)
    return r  # type: ignore


@fl.with_fiat_attributes(
    max_value__range=(0.0, 255.0),
    block_size__range=(3, 51),
    block_size__validator=_block_size_validator,
    c__range=(-50.0, 50.0),
)
def adaptive_threshold(
    image: ImageU8_GRAY,
    max_value: float = 255.0,
    method: AdaptiveMethod = AdaptiveMethod.ADAPTIVE_THRESH_GAUSSIAN_C,
    type: AdaptiveThresholdType = AdaptiveThresholdType.THRESH_BINARY,
    block_size: int = 11,
    c: float = 2.0,
) -> ImageU8_GRAY:
    """Per-pixel threshold whose level depends on a local neighbourhood.

    **When to use:** When lighting varies across the image (shadows, gradients).
    Robust where a single global threshold fails.

    **Parameters:**
    - `max_value`: value assigned to pixels above the local threshold.
    - `method`: how the local threshold is computed (mean or Gaussian-weighted).
    - `type`: BINARY or BINARY_INV; other modes are not supported by cv2.
    - `block_size`: side of the local neighbourhood. Must be odd, >= 3.
    - `c`: constant subtracted from the local mean. Higher = stricter.

    **See also:** `threshold` (global threshold), `gaussian_blur`.

    **OpenCV docs:** [cv2.adaptiveThreshold](https://docs.opencv.org/4.13.0/d7/d1b/group__imgproc__misc.html#ga72b913f352e4a1b1b397736707afcde3)
    """
    r = cv2.adaptiveThreshold(image, max_value, method.value, type.value, block_size, c)
    return r  # type: ignore
