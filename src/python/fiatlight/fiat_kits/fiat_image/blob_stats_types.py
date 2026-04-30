"""Typed representation for connected-component blob statistics.

A `BlobStats` value is an `(N, 5)` int32 ndarray where each row is
`(x, y, w, h, area)` — the native form of cv2's
`connectedComponentsWithStats` `stats` output (one row per label,
including row 0 = background).
"""

import numpy as np

from fiatlight.fiat_types.typename_utils import documented_newtype


BlobStats = documented_newtype(
    "BlobStats",
    np.ndarray,
    "Per-component blob statistics as an (N, 5) int32 ndarray, "
    "rows (x, y, w, h, area). Row 0 is the background blob.",
)
