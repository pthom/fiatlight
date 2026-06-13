import numpy as np

from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_kits.fiat_image import Rect2D, Image


@with_fiat_attributes(
    fiat_tags=["geometry"],
)
def image_roi(img: Image, rect: Rect2D) -> Image:
    """Crop a rectangular region of interest from an image.

    **When to use:** Extract a rectangular patch from an image, e.g. for cropping or zooming into a specific area.

    **Parameters:**
    - `img`: input image.
    - `rect`: rectangle specifying the ROI as (x, y, w, h).

    **Note:** This wrapper returns a copy of the ROI region (using numpy.copy).
    """
    shape = img.shape
    img_width, img_height = shape[0], shape[1]
    x, y, w, h = rect.x, rect.y, rect.w, rect.h
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > img_width or y + h > img_height:
        raise ValueError(f"Invalid ROI rectangle {rect} for image of shape {shape}")

    r = np.copy(img[y : y + h, x : x + w])
    return r  # type: ignore
