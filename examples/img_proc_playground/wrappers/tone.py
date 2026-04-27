"""Tone / contrast wrappers for the image-processing playground.

These adjust the brightness, contrast or color mapping of an image without
changing its geometry.
"""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageBgr, ImageU8, ImageU8_GRAY

import cv2

from examples.img_proc_playground.fiat_cv_enums import ColorMap


@fl.with_fiat_attributes(fiat_tags=["tone", "cv2.imgproc"])
def equalize_hist(image: ImageU8_GRAY) -> ImageU8_GRAY:
    """Global histogram equalization on a grayscale image.

    **When to use:** Stretch contrast on a low-contrast image whose
    histogram is concentrated in a narrow range. For uneven lighting,
    prefer `clahe`.

    **See also:** `clahe`.

    **OpenCV docs:** [cv2.equalizeHist](https://docs.opencv.org/4.13.0/d6/dc7/group__imgproc__hist.html#ga7e54091f0c937d49bf84152a16f76d6e)
    """
    r = cv2.equalizeHist(image)
    return r  # type: ignore


@fl.with_fiat_attributes(
    clip_limit__range=(0.5, 40.0),
    tile_grid_size__range=(1, 32),
    fiat_tags=["tone", "cv2.imgproc"],
)
def clahe(
    image: ImageU8_GRAY,
    clip_limit: float = 2.0,
    tile_grid_size: int = 8,
) -> ImageU8_GRAY:
    """Contrast-Limited Adaptive Histogram Equalization on a grayscale image.

    **When to use:** Boost local contrast where lighting varies across the
    image. Less prone to over-amplifying noise than plain `equalize_hist`.

    **Parameters:**
    - `clip_limit`: clipping threshold for histogram bins. Higher = more
      aggressive contrast boost.
    - `tile_grid_size`: side of the local tile grid (e.g. 8 → 8×8 tiles).

    **See also:** `equalize_hist`.

    **OpenCV docs:** [cv2.createCLAHE](https://docs.opencv.org/4.13.0/d6/db6/classcv_1_1CLAHE.html)
    """
    op = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
    r = op.apply(image)
    return r  # type: ignore


@fl.with_fiat_attributes(fiat_tags=["color", "tone", "cv2.imgproc"])
def apply_color_map(image: ImageU8_GRAY, colormap: ColorMap = ColorMap.VIRIDIS) -> ImageBgr:
    """Map a single-channel image to color via a built-in cv2 color map.

    **When to use:** Visualize a grayscale image (depth, heat, gradient
    magnitude, …) with a perceptually meaningful color ramp.

    Output is a BGR image; insert a `color_convert(BGR→RGB)` downstream
    if the rest of the pipeline expects RGB.

    **OpenCV docs:** [cv2.applyColorMap](https://docs.opencv.org/4.13.0/d3/d50/group__imgproc__colormap.html#gadf478a5e5ff49d8aa24e726ea6f65d15)
    """
    r = cv2.applyColorMap(image, colormap.value)
    return r  # type: ignore


@fl.with_fiat_attributes(
    alpha__range=(0.0, 4.0),
    beta__range=(-128.0, 128.0),
    fiat_tags=["tone", "cv2.core"],
)
def convert_scale_abs(image: ImageU8, alpha: float = 1.0, beta: float = 0.0) -> ImageU8:
    """Linear contrast / brightness adjustment: `|alpha*src + beta|` clipped to U8.

    **When to use:** Quick brightness / contrast tweak. `alpha > 1` boosts
    contrast, `alpha < 1` flattens it; `beta` shifts brightness.

    **Parameters:**
    - `alpha`: gain (contrast multiplier).
    - `beta`: bias (brightness offset).

    **OpenCV docs:** [cv2.convertScaleAbs](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#ga3460e9c9f37b563ab9dd550c4d8c4e7d)
    """
    r = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return r  # type: ignore
