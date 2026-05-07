"""Typed representation for a list of 2D line segments.

A `Lines2D` value is an `(N, 4)` int32 ndarray of pixel-endpoint pairs
`(x1, y1, x2, y2)`. cv2's `HoughLinesP` natively returns `(N, 1, 4)`;
wrappers should `.reshape(-1, 4)` and cast to int before producing a
`Lines2D` so the type is consistent for consumers.
"""

from typing import NewType

import numpy as np


Lines2D = NewType("Lines2D", np.ndarray)
Lines2D.__doc__ = (
    "List of 2D line segments as an (N, 4) int32 ndarray, each row "
    "(x1, y1, x2, y2). Returned by HoughLinesP and consumed by drawing helpers."
)
