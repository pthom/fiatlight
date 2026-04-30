"""Typed representation for OpenCV contours.

A `Contours` value is a list of contours in the native cv2 form:
each contour is an `(N, 1, 2) int32` ndarray. This is what
`cv2.findContours` returns and what `cv2.drawContours` accepts, so no
conversion happens at the boundary.
"""

from typing import NewType
import numpy as np


Contours = NewType("Contours", list[np.ndarray])
Contours.__doc__ = (
    "List of OpenCV contours. Each contour is an (N, 1, 2) int32 ndarray "
    "(the form returned by cv2.findContours and accepted by cv2.drawContours)."
)
