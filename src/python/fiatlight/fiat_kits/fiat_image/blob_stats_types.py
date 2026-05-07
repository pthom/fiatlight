"""Typed representation for connected-component blob statistics.

A `BlobStats` value is an `(N, 5)` int32 ndarray where each row is
`(x, y, w, h, area)` — the native form of cv2's
`connectedComponentsWithStats` `stats` output (one row per label,
including row 0 = background).
"""

from typing import NewType

import numpy as np


BlobStats = NewType("BlobStats", np.ndarray)
BlobStats.__doc__ = (
    "Per-component blob statistics as an (N, 5) int32 ndarray, "
    "rows (x, y, w, h, area). Row 0 is the background blob."
)
