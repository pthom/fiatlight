"""Typed representations for affine and perspective transform matrices.

`Matrix2x3` is the (2, 3) float64 ndarray returned by
`cv2.getRotationMatrix2D` / `cv2.getAffineTransform` and consumed by
`cv2.warpAffine`. `Matrix3x3` is the (3, 3) float64 ndarray returned by
`cv2.getPerspectiveTransform` / `cv2.findHomography` and consumed by
`cv2.warpPerspective`.

Both are read-only outputs in the playground: the user shapes them via
the producing node's parameters (angle, scale, source/target points).
"""

from typing import NewType

import numpy as np


Matrix2x3 = NewType("Matrix2x3", np.ndarray)
Matrix2x3.__doc__ = (
    "Affine transform matrix as a (2, 3) float64 ndarray. Returned by "
    "cv2.getRotationMatrix2D / cv2.getAffineTransform and consumed by cv2.warpAffine."
)

Matrix3x3 = NewType("Matrix3x3", np.ndarray)
Matrix3x3.__doc__ = (
    "Perspective transform matrix as a (3, 3) float64 ndarray. Returned by "
    "cv2.getPerspectiveTransform / cv2.findHomography and consumed by cv2.warpPerspective."
)
