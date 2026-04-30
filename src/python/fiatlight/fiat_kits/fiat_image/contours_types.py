"""Typed representation for OpenCV contours.

A `Contours` value is a list of contours in the native cv2 form:
each contour is an `(N, 1, 2) int32` ndarray. This is what
`cv2.findContours` returns and what `cv2.drawContours` accepts, so no
conversion happens at the boundary.

`ContoursHierarchy` is the companion array returned by
`cv2.findContours`: shape `(1, N, 4) int32`, where each row is
`[next, prev, first_child, parent]`. Required by `cv2.drawContours`
when filtering by tree depth via `maxLevel`.
"""

from typing import NewType
import numpy as np


Contours = NewType("Contours", list[np.ndarray])
Contours.__doc__ = (
    "List of OpenCV contours. Each contour is an (N, 1, 2) int32 ndarray "
    "(the form returned by cv2.findContours and accepted by cv2.drawContours)."
)


ContoursHierarchy = NewType("ContoursHierarchy", np.ndarray)
ContoursHierarchy.__doc__ = (
    "Hierarchy array companion to a Contours value. Shape (1, N, 4) int32, "
    "rows are [next, prev, first_child, parent]. Used by cv2.drawContours "
    "with maxLevel to draw outer contours only, outer + immediate holes, etc."
)
