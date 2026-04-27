"""Geometric-transform wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8

import cv2

from examples.img_proc_playground.fiat_cv_enums import InterpolationFlag


@fl.with_fiat_attributes(
    fx__range=(0.05, 4.0),
    fy__range=(0.0, 4.0),
)
def resize(
    image: ImageU8,
    fx: float = 0.5,
    fy: float = 0.0,
    interpolation: InterpolationFlag = InterpolationFlag.INTER_LINEAR,
) -> ImageU8:
    """Resize an image by a per-axis scale factor.

    **When to use:** Downscale before slow ops (bilateral filter on 4K) to
    keep the live-tuning loop responsive. Upscale for display.

    **Parameters:**
    - `fx`: horizontal scale factor. 0.5 = half width.
    - `fy`: vertical scale factor. 0.0 = lock to `fx` (uniform scale).
    - `interpolation`: how new pixels are sampled. `INTER_AREA` is best for
      downscaling; `INTER_CUBIC` / `INTER_LANCZOS4` for upscaling.

    **OpenCV docs:** [cv2.resize](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html#ga47a974309e9102f5f08231edc7e7529d)
    """
    if fy == 0.0:
        fy = fx
    r = cv2.resize(image, (0, 0), fx=fx, fy=fy, interpolation=interpolation.value)
    return r  # type: ignore
