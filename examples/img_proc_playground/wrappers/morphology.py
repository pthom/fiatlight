"""Morphology wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8_GRAY

import cv2

from examples.img_proc_playground.fiat_cv_enums import MorphShape


@fl.with_fiat_attributes(kernel_size__range=(1, 10), iterations__range=(1, 10))
def dilate(
    image: ImageU8_GRAY,
    kernel_size: int = 2,
    morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE,
    iterations: int = 1,
) -> ImageU8_GRAY:
    """Dilate the image using the specified kernel shape and size.

    **When to use:** Thicken bright regions in a binary or grayscale image.
    Common after edge detection to make edges more visible.

    **Parameters:**
    - `kernel_size`: side of the square structuring element. 1 = no-op.
    - `morph_shape`: shape of the structuring element.
    - `iterations`: number of times the dilation is applied.

    **See also:** `erode` (opposite operation), `canny`.

    **OpenCV docs:** [cv2.dilate](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c)
    """
    kernel = cv2.getStructuringElement(morph_shape.value, (kernel_size, kernel_size))
    r = cv2.dilate(image, kernel, iterations=iterations)
    return r  # type: ignore


@fl.with_fiat_attributes(kernel_size__range=(1, 10), iterations__range=(1, 10))
def erode(
    image: ImageU8_GRAY,
    kernel_size: int = 2,
    morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE,
    iterations: int = 1,
) -> ImageU8_GRAY:
    """Erode the image using the specified kernel shape and size.

    **When to use:** Shrink bright regions. Useful to remove small noise
    spots, or as the dual of dilation in opening / closing pipelines.

    **Parameters:**
    - `kernel_size`: side of the square structuring element. 1 = no-op.
    - `morph_shape`: shape of the structuring element.
    - `iterations`: number of times the erosion is applied.

    **See also:** `dilate` (opposite operation).

    **OpenCV docs:** [cv2.erode](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#gaeb1e0c1033e3f6b891a25d0511362aeb)
    """
    kernel = cv2.getStructuringElement(morph_shape.value, (kernel_size, kernel_size))
    r = cv2.erode(image, kernel, iterations=iterations)
    return r  # type: ignore
