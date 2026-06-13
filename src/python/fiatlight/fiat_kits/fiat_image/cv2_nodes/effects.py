"""Photo-effect / segmentation wrappers that produce multi-output or
seed-based pipelines (cv2.photo + cv2.imgproc segmentation)."""
from typing import NamedTuple

import cv2
import numpy as np

from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_kits.fiat_image import ImageBgr, ImageU8, ImageU8_3, ImageU8_GRAY, Point2D, Rect2D
from fiatlight.fiat_types import ColorRgb


class PencilSketchResult(NamedTuple):
    """Two-pin output of `pencilSketch`: the pencil-shading (gray) and a
    color stylization of the source."""

    gray: ImageU8_GRAY
    color: ImageBgr


@with_fiat_attributes(
    invoke_async=True,
    sigma_s__range=(1.0, 200.0),
    sigma_r__range=(0.0, 1.0),
    shade_factor__range=(0.0, 0.1),
    fiat_tags=["filter", "photo"],
)
def pencilSketch(
    image: ImageU8_3,
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
    return PencilSketchResult(gray=gray, color=color)  # type: ignore


@with_fiat_attributes(
    lo_diff__range=(0, 100),
    up_diff__range=(0, 100),
    fiat_tags=["segmentation"],
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


@with_fiat_attributes(
    iter_count__range=(1, 10),
    invoke_async=True,
    fiat_tags=["segmentation"],
)
def grabCut(
    image: ImageBgr,
    rect: Rect2D,
    iter_count: int = 3,
) -> ImageU8_GRAY:
    """Foreground segmentation by GrabCut, seeded by a bounding rectangle.

    **When to use:** Pull an object out of a photo when you can roughly
    bbox it. Output is a binary mask: 255 inside foreground, 0 elsewhere.
    Pair with `bitwise_and` against the source image to extract.

    Slow on big images; this wrapper is `invoke_async`.

    **Parameters:**
    - `rect`: bounding box of the probable foreground object.
    - `iter_count`: GrabCut iterations (more = slower + cleaner).

    **OpenCV docs:** [cv2.grabCut](https://docs.opencv.org/4.13.0/d3/d47/group__imgproc__segmentation.html#ga909c1dda50efcbeaa3ce126be862b37f)
    """
    if rect.w < 2 or rect.h < 2:
        return np.zeros(image.shape[:2], dtype=np.uint8)  # type: ignore
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    bgd_model = np.zeros((1, 65), dtype=np.float64)
    fgd_model = np.zeros((1, 65), dtype=np.float64)
    cv2.grabCut(
        image,
        mask,
        (rect.x, rect.y, rect.w, rect.h),
        bgd_model,
        fgd_model,
        iter_count,
        cv2.GC_INIT_WITH_RECT,
    )
    out = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    return out  # type: ignore


@with_fiat_attributes(fiat_tags=["segmentation"])
def watershed(
    image: ImageBgr,
    markers: ImageU8_GRAY,
) -> ImageU8_GRAY:
    """Marker-based watershed segmentation.

    **When to use:** Split touching objects when you can pre-mark seed
    regions (e.g. via thresholding + connected-component labels mapped
    to small marker regions). Output: per-pixel region label as U8
    (clipped to 0-255; -1 boundary pixels become 255).

    **Parameters:**
    - `markers`: input marker image. Each non-zero pixel is treated as
      a seed region label. Background should be labelled 1; unknown
      regions 0.

    **OpenCV docs:** [cv2.watershed](https://docs.opencv.org/4.13.0/d3/d47/group__imgproc__segmentation.html#ga3267243e4d3f95165d55a618c65ac6e1)
    """
    m32 = markers.astype(np.int32)
    cv2.watershed(image, m32)
    out = np.clip(m32, 0, 255).astype(np.uint8)
    return out  # type: ignore
