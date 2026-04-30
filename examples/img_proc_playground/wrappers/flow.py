"""Optical-flow wrappers for the image-processing playground."""
from typing import NamedTuple

import cv2
import numpy as np

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8_GRAY, Points2D


class SparseFlowResult(NamedTuple):
    """Two-pin output of `calcOpticalFlowPyrLK`: tracked points + per-point
    track status (1 = found in next frame, 0 = lost)."""

    next_pts: Points2D
    status: Points2D  # (N, 2) where col 0 = status flag, col 1 = err (rounded)


@fl.with_fiat_attributes(
    win_size__range=(3, 51),
    max_level__range=(0, 6),
    max_iter__range=(1, 100),
    epsilon__range=(0.001, 1.0),
    epsilon__slider_logarithmic=True,
    fiat_tags=["features", "tracking", "cv2.video"],
)
def calcOpticalFlowPyrLK(
    prev_image: ImageU8_GRAY,
    next_image: ImageU8_GRAY,
    prev_points: Points2D,
    win_size: int = 21,
    max_level: int = 3,
    max_iter: int = 30,
    epsilon: float = 0.01,
) -> SparseFlowResult:
    """Sparse pyramidal Lucas-Kanade tracker.

    **When to use:** Track a set of points (typically from
    `goodFeaturesToTrack`) from one frame to the next. Output points
    with `status[:, 0] == 0` were lost — filter before drawing.

    **Parameters:**
    - `win_size`: search window side (odd-ish; cv2 uses (size, size)).
    - `max_level`: pyramid depth (0 = no pyramid).
    - `max_iter`, `epsilon`: termination criteria.

    **See also:** `goodFeaturesToTrack`, `drawPoints`.

    **OpenCV docs:** [cv2.calcOpticalFlowPyrLK](https://docs.opencv.org/4.13.0/dc/d6b/group__video__track.html#ga473e4b886d0bcc6b65831eb88ed93323)
    """
    if len(prev_points) == 0:
        return SparseFlowResult(
            next_pts=Points2D(np.empty((0, 2), dtype=np.int32)),
            status=Points2D(np.empty((0, 2), dtype=np.int32)),
        )
    p0 = prev_points.astype(np.float32).reshape(-1, 1, 2)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iter, epsilon)
    p1, st, err = cv2.calcOpticalFlowPyrLK(
        prev_image, next_image, p0, None, winSize=(win_size, win_size), maxLevel=max_level, criteria=crit
    )
    next_pts = Points2D(p1.reshape(-1, 2).round().astype(np.int32))
    status = np.zeros((len(prev_points), 2), dtype=np.int32)
    if st is not None:
        status[:, 0] = st.reshape(-1).astype(np.int32)
    if err is not None:
        status[:, 1] = err.reshape(-1).round().astype(np.int32)
    return SparseFlowResult(next_pts=next_pts, status=Points2D(status))
