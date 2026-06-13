"""Connected-components wrappers for the playground (spec §12.3)."""
from typing import NamedTuple

import cv2
import numpy as np

from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_kits.fiat_image import (
    BlobStats,
    ImageU8_GRAY,
    LabelImage,
    Points2D,
)


class ConnectedComponentsResult(NamedTuple):
    """Two-pin output of `connectedComponents`."""

    num_labels: int
    labels: LabelImage


class ConnectedComponentsWithStatsResult(NamedTuple):
    """Four-pin output of `connectedComponentsWithStats`."""

    num_labels: int
    labels: LabelImage
    stats: BlobStats
    centroids: Points2D


@with_fiat_attributes(
    connectivity__range=(4, 8),
    fiat_tags=["blobs", "cv2.imgproc"],
)
def connectedComponents(
    image: ImageU8_GRAY,
    connectivity: int = 8,
) -> ConnectedComponentsResult:
    """Label each connected component of a binary image.

    **When to use:** Find separate blobs in a thresholded mask. Output
    is the label image (each pixel holds its component ID) plus the
    total label count (background included).

    **Parameters:**
    - `connectivity`: 4 or 8.

    **See also:** `connectedComponentsWithStats`, `threshold`.

    **OpenCV docs:** [cv2.connectedComponents](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#gaedef8c7340499ca391d459122e51bef5)
    """
    n, labels = cv2.connectedComponents(image, connectivity=connectivity)
    return ConnectedComponentsResult(
        num_labels=int(n),
        labels=LabelImage(labels.astype(np.int32)),
    )


@with_fiat_attributes(
    connectivity__range=(4, 8),
    fiat_tags=["blobs", "cv2.imgproc"],
)
def connectedComponentsWithStats(
    image: ImageU8_GRAY,
    connectivity: int = 8,
) -> ConnectedComponentsWithStatsResult:
    """Label each connected component AND compute per-blob stats / centroids.

    **When to use:** Blob analysis — filter by area, find centers, draw
    bounding boxes per component.

    Output:
    - `num_labels`: total label count (row 0 = background).
    - `labels`: per-pixel component ID image.
    - `stats`: `(N, 5)` int array of `(x, y, w, h, area)` per label.
    - `centroids`: `(N, 2)` int point array of per-label center.

    Centroids are returned as integer `Points2D` (rounded from cv2's
    float centroids); for sub-pixel precision call cv2 directly.

    **OpenCV docs:** [cv2.connectedComponentsWithStats](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#ga107a78bf7cd25dec05fb4dfc5c9e765f)
    """
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=connectivity)
    return ConnectedComponentsWithStatsResult(
        num_labels=int(n),
        labels=LabelImage(labels.astype(np.int32)),
        stats=BlobStats(stats.astype(np.int32)),
        centroids=Points2D(centroids.round().astype(np.int32)),
    )
