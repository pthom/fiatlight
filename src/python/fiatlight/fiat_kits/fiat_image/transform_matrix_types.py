"""Typed representations for affine and perspective transform matrices.

`Matrix2x3` is the (2, 3) float64 ndarray returned by
`cv2.getRotationMatrix2D` / `cv2.getAffineTransform` and consumed by
`cv2.warpAffine`. `Matrix3x3` is the (3, 3) float64 ndarray returned by
`cv2.getPerspectiveTransform` / `cv2.findHomography` and consumed by
`cv2.warpPerspective`.

Both are read-only outputs in the playground: the user shapes them via
the producing node's parameters (angle, scale, source/target points).
"""

import numpy as np

from fiatlight.fiat_types.typename_utils import documented_newtype


Matrix2x3 = documented_newtype(
    "Matrix2x3",
    np.ndarray,
    "Affine transform matrix as a (2, 3) float64 ndarray. Returned by "
    "cv2.getRotationMatrix2D / cv2.getAffineTransform and consumed by cv2.warpAffine.",
)

Matrix3x3 = documented_newtype(
    "Matrix3x3",
    np.ndarray,
    "Perspective transform matrix as a (3, 3) float64 ndarray. Returned by "
    "cv2.getPerspectiveTransform / cv2.findHomography and consumed by cv2.warpPerspective.",
)
