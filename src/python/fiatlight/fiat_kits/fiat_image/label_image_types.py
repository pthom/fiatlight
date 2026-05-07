"""Typed representation for a connected-components label image.

A `LabelImage` is the (H, W) int32 ndarray returned by
`cv2.connectedComponents`. Each pixel holds a small integer (0 = background,
1..N = component IDs).
"""

from typing import NewType

import numpy as np


LabelImage = NewType("LabelImage", np.ndarray)
LabelImage.__doc__ = (
    "Connected-components label image as a (H, W) int32 ndarray. "
    "0 = background, 1..N = component IDs. Returned by cv2.connectedComponents."
)
