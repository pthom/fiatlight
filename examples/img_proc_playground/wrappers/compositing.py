"""Compositing wrappers for the image-processing playground."""
from fiatlight.fiat_kits.fiat_image import ImageU8

import cv2


def bitwise_and(image_a: ImageU8, image_b: ImageU8) -> ImageU8:
    """Per-pixel bitwise AND of two images.

    **When to use:** Mask out parts of an image — e.g. AND with a binary
    mask to keep only the regions selected by the mask.

    **Parameters:**
    - `image_a`, `image_b`: two images of compatible shape and dtype.

    **See also:** `bitwise_or`, `threshold` (to build a mask).

    **OpenCV docs:** [cv2.bitwise_and](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga60b4d04b251ba5eb1392c34425497e14)
    """
    r = cv2.bitwise_and(image_a, image_b)
    return r  # type: ignore


def bitwise_or(image_a: ImageU8, image_b: ImageU8) -> ImageU8:
    """Per-pixel bitwise OR of two images.

    **When to use:** Combine two masks, or overlay a bright drawing on an
    image where both inputs share the bright value.

    **Parameters:**
    - `image_a`, `image_b`: two images of compatible shape and dtype.

    **See also:** `bitwise_and`.

    **OpenCV docs:** [cv2.bitwise_or](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#gab85523db362a4e26ff0c703793a719b4)
    """
    r = cv2.bitwise_or(image_a, image_b)
    return r  # type: ignore
