"""Compositing wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8

import cv2


@fl.with_fiat_attributes(fiat_tags=["compositing", "cv2.core"])
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


@fl.with_fiat_attributes(fiat_tags=["compositing", "cv2.core"])
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


@fl.with_fiat_attributes(fiat_tags=["compositing", "cv2.core"])
def bitwise_xor(image_a: ImageU8, image_b: ImageU8) -> ImageU8:
    """Per-pixel bitwise XOR of two images.

    **When to use:** Highlight differences between two binary masks, or
    create stripe patterns from overlapping regions.

    **OpenCV docs:** [cv2.bitwise_xor](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga84b2d8188ce506593dcc3f8cd00e8e2c)
    """
    r = cv2.bitwise_xor(image_a, image_b)
    return r  # type: ignore


@fl.with_fiat_attributes(fiat_tags=["compositing", "cv2.core"])
def bitwise_not(image: ImageU8) -> ImageU8:
    """Per-pixel bitwise NOT — invert the image.

    **When to use:** Invert a mask, or produce a "negative" of a U8 image.

    **OpenCV docs:** [cv2.bitwise_not](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga0002cf8b418479f4cb49a75442baee2f)
    """
    r = cv2.bitwise_not(image)
    return r  # type: ignore


@fl.with_fiat_attributes(
    alpha__range=(0.0, 2.0),
    beta__range=(0.0, 2.0),
    gamma__range=(-128.0, 128.0),
    fiat_tags=["compositing", "cv2.core"],
)
def addWeighted(
    image_a: ImageU8,
    image_b: ImageU8,
    alpha: float = 0.5,
    beta: float = 0.5,
    gamma: float = 0.0,
) -> ImageU8:
    """Linear blend of two images: `result = alpha*A + beta*B + gamma`.

    **When to use:** Cross-fade between images, overlay one image on
    another, or boost / dim with a bias.

    **Parameters:**
    - `alpha`: weight for `image_a`.
    - `beta`: weight for `image_b`.
    - `gamma`: scalar bias added to the sum.

    **OpenCV docs:** [cv2.addWeighted](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#gafafb2513349db3bcff51f54ee5592a19)
    """
    r = cv2.addWeighted(image_a, alpha, image_b, beta, gamma)
    return r  # type: ignore


@fl.with_fiat_attributes(fiat_tags=["compositing", "cv2.core"])
def absdiff(image_a: ImageU8, image_b: ImageU8) -> ImageU8:
    """Per-pixel `|A - B|` — absolute difference of two images.

    **When to use:** Change detection between successive frames, or
    visualizing the residual between an image and a filtered version.

    **OpenCV docs:** [cv2.absdiff](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga6fef31bc8c4071cbc114a758a2b79c14)
    """
    r = cv2.absdiff(image_a, image_b)
    return r  # type: ignore
