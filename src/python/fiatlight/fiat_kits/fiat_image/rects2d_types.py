"""Typed representation for a list of axis-aligned rectangles.

A `Rects2D` value is an `(N, 4)` int32 ndarray of `(x, y, w, h)` rows —
the native form of `cv2.boundingRect` (one rect at a time, stacked).
"""

import numpy as np

from fiatlight.fiat_types.typename_utils import documented_newtype


Rects2D = documented_newtype(
    "Rects2D",
    np.ndarray,
    "List of axis-aligned rectangles as an (N, 4) int32 ndarray, "
    "each row (x, y, w, h). Returned by per-contour boundingRect.",
)
