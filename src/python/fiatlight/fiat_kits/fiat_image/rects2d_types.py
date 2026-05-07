"""Typed representation for a list of axis-aligned rectangles.

A `Rects2D` value is an `(N, 4)` int32 ndarray of `(x, y, w, h)` rows —
the native form of `cv2.boundingRect` (one rect at a time, stacked).
"""

from typing import NewType

import numpy as np


Rects2D = NewType("Rects2D", np.ndarray)
Rects2D.__doc__ = (
    "List of axis-aligned rectangles as an (N, 4) int32 ndarray, "
    "each row (x, y, w, h). Returned by per-contour boundingRect."
)
