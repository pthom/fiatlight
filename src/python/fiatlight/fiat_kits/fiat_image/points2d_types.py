"""Typed representation for a list of 2D points.

A `Points2D` value is an `(N, 2)` ndarray of pixel coordinates. This is
the natural form for keypoint sets returned by feature detectors and
consumed by drawing helpers. cv2's `goodFeaturesToTrack` returns
`(N, 1, 2)` float32 — wrappers should `.reshape(-1, 2)` and cast to int
before producing a `Points2D` so the type is consistent for consumers.
"""

from typing import NewType
import numpy as np


Points2D = NewType("Points2D", np.ndarray)
Points2D.__doc__ = (
    "List of 2D pixel coordinates as an (N, 2) int32 ndarray. "
    "Returned by feature detectors (goodFeaturesToTrack, cornerHarris peaks, "
    "Hough centers) and consumed by drawing helpers."
)
