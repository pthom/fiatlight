"""Typed representation for a list of 2D circles.

A `Circles2D` value is an `(N, 3)` int32 ndarray of `(cx, cy, r)` triples
— the natural form for circle detectors. cv2's `HoughCircles` returns
`(1, N, 3)` float32; wrappers should `.reshape(-1, 3)` and cast to int
before producing a `Circles2D`.
"""

from typing import NewType

import numpy as np


Circles2D = NewType("Circles2D", np.ndarray)
Circles2D.__doc__ = (
    "List of 2D circles as an (N, 3) int32 ndarray, each row (cx, cy, r). "
    "Returned by HoughCircles and consumed by drawing helpers."
)
