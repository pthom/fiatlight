"""Typed representation for a list of rotated rectangles / ellipse parameters.

A `RotatedRects2D` value is an `(N, 5)` float32 ndarray of
`(cx, cy, w, h, angle_degrees)` rows — the parametric form shared by
`cv2.minAreaRect` (rotated bounding box) and `cv2.fitEllipse` (best-fit
ellipse). Either rendering applies; pick the renderer that matches the
intent (`drawRotatedRects` or `drawEllipses`).
"""

import numpy as np

from fiatlight.fiat_types.typename_utils import documented_newtype


RotatedRects2D = documented_newtype(
    "RotatedRects2D",
    np.ndarray,
    "List of rotated rectangles / ellipses as an (N, 5) float32 ndarray, "
    "each row (cx, cy, w, h, angle). Returned by minAreaRect / fitEllipse.",
)
