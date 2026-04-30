"""Typed representation for a list of 2D points.

A `Points2D` value is an `(N, 2)` int32 ndarray of pixel coordinates —
the natural form for keypoint sets returned by feature detectors and
consumed by drawing helpers. cv2's `goodFeaturesToTrack` returns
`(N, 1, 2)` float32; wrappers should `.reshape(-1, 2)` and cast to int
before producing a `Points2D` so the type is consistent for consumers.
"""

import numpy as np

from fiatlight.fiat_types.typename_utils import documented_newtype


Points2D = documented_newtype(
    "Points2D",
    np.ndarray,
    "List of 2D pixel coordinates as an (N, 2) int32 ndarray. "
    "Returned by feature detectors (goodFeaturesToTrack, cornerHarris peaks, "
    "Hough centers) and consumed by drawing helpers.",
)
