"""Photo-effect / segmentation wrappers that produce multi-output or
seed-based pipelines (cv2.photo + cv2.imgproc segmentation)."""
from typing import NamedTuple

import cv2
import numpy as np

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageBgr, ImageU8, ImageU8_GRAY, Point2D
from fiatlight.fiat_types import ColorRgb


class PencilSketchResult(NamedTuple):
    """Two-pin output of `pencilSketch`: the pencil-shading (gray) and a
    color stylization of the source."""

    gray: ImageU8_GRAY
    color: ImageBgr


@fl.with_fiat_attributes(
    invoke_async=True,
    sigma_s__range=(1.0, 200.0),
    sigma_r__range=(0.0, 1.0),
    shade_factor__range=(0.0, 0.1),
    fiat_tags=["filter", "photo", "cv2.photo"],
)
def pencilSketch(
    image: ImageBgr,
    sigma_s: float = 60.0,
    sigma_r: float = 0.07,
    shade_factor: float = 0.05,
) -> PencilSketchResult:
    """Pencil-sketch + colour stylization in one pass.

    **When to use:** "Drawn by hand" effect on a photo. Gray output is
    the pencil rendering; color output is a stylized version of the
    same input.

    **Parameters:**
    - `sigma_s`: spatial scale.
    - `sigma_r`: range scale.
    - `shade_factor`: mixing factor between gray and source.

    **See also:** `stylization`, `edgePreservingFilter`.

    **OpenCV docs:** [cv2.pencilSketch](https://docs.opencv.org/4.13.0/df/dac/group__photo__render.html#gae5930dd822c713b36f8529b21ddebd0c)
    """
    gray, color = cv2.pencilSketch(image, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=shade_factor)
    return PencilSketchResult(gray=gray, color=color)


@fl.with_fiat_attributes(
    lo_diff__range=(0, 100),
    up_diff__range=(0, 100),
    fiat_tags=["segmentation", "cv2.imgproc"],
)
def floodFill(
    image: ImageU8,
    seed: Point2D,
    new_color: ColorRgb = ColorRgb((0, 255, 0)),
    lo_diff: int = 10,
    up_diff: int = 10,
) -> ImageU8:
    """Flood-fill from `seed` with `new_color`.

    **When to use:** Quick seed-based segmentation — paint a connected
    region whose pixels are within `lo_diff` / `up_diff` of the seed
    pixel value.

    **Parameters:**
    - `seed`: starting (x, y) pixel.
    - `new_color`: replacement color (RGB; for grayscale input only the
      red channel is used).
    - `lo_diff`, `up_diff`: maximum lower / upper brightness difference
      from the seed pixel that still belongs to the region.

    **OpenCV docs:** [cv2.floodFill](https://docs.opencv.org/4.13.0/d7/d1b/group__imgproc__misc.html#gaf1f55a048f8a45bc3383586e80b1f0d0)
    """
    out = np.ascontiguousarray(image).copy()
    h, w = out.shape[:2]
    if not (0 <= seed.x < w and 0 <= seed.y < h):
        return out  # type: ignore
    mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    if out.ndim == 2:
        new_val: tuple[int, ...] = (int(new_color[0]),)
    else:
        new_val = tuple(int(c) for c in new_color)
    cv2.floodFill(out, mask, (seed.x, seed.y), new_val, (lo_diff,) * len(new_val), (up_diff,) * len(new_val))
    return out  # type: ignore
