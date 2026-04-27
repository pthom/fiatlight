"""Geometric-transform wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8

import cv2

from examples.img_proc_playground.fiat_cv_enums import BorderType, FlipCode, InterpolationFlag, RotateCode


@fl.with_fiat_attributes(
    fx__range=(0.05, 4.0),
    fy__range=(0.0, 4.0),
    fiat_tags=["geometry", "cv2.imgproc"],
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


@fl.with_fiat_attributes(fiat_tags=["geometry", "cv2.core"])
def flip(image: ImageU8, flip_code: FlipCode = FlipCode.HORIZONTAL) -> ImageU8:
    """Mirror an image around an axis.

    **Parameters:**
    - `flip_code`: `HORIZONTAL` mirrors left-right, `VERTICAL` mirrors
      top-bottom, `BOTH` is a 180° rotation.

    **See also:** `rotate`.

    **OpenCV docs:** [cv2.flip](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#gaca7be533e3dac7feb70fc60635adf441)
    """
    r = cv2.flip(image, flip_code.value)
    return r  # type: ignore


@fl.with_fiat_attributes(fiat_tags=["geometry", "cv2.core"])
def rotate(image: ImageU8, rotate_code: RotateCode = RotateCode.ROTATE_90_CW) -> ImageU8:
    """Rotate an image by a multiple of 90°.

    **When to use:** Cheap, lossless quarter-turn rotation. For arbitrary
    angles, use `cv2.warpAffine` (not yet wrapped — see v1 hints in the spec).

    **OpenCV docs:** [cv2.rotate](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga4ad01c0978b65c64cb8d8d04c4a2b6e9)
    """
    r = cv2.rotate(image, rotate_code.value)
    return r  # type: ignore


@fl.with_fiat_attributes(
    top__range=(0, 200),
    bottom__range=(0, 200),
    left__range=(0, 200),
    right__range=(0, 200),
    constant_value__range=(0, 255),
    fiat_tags=["geometry", "cv2.core"],
)
def copy_make_border(
    image: ImageU8,
    top: int = 10,
    bottom: int = 10,
    left: int = 10,
    right: int = 10,
    border_type: BorderType = BorderType.BORDER_REFLECT_101,
    constant_value: int = 0,
) -> ImageU8:
    """Add a border around the image.

    **When to use:** Pad before convolutions that need extra context, or
    just to frame the image visually. With `BORDER_CONSTANT`, fill the new
    pixels with `constant_value` (replicated across channels).

    **Parameters:**
    - `top` / `bottom` / `left` / `right`: border size in pixels.
    - `border_type`: how the new pixels are filled.
    - `constant_value`: only used with `BORDER_CONSTANT`.

    **OpenCV docs:** [cv2.copyMakeBorder](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga2ac1049c2c3dd25c2b41bffe17658a36)
    """
    r = cv2.copyMakeBorder(
        image, top, bottom, left, right, border_type.value, value=(constant_value, constant_value, constant_value)
    )
    return r  # type: ignore
