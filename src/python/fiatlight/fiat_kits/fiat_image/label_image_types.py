"""Typed representation for a connected-components label image.

A `LabelImage` is the (H, W) int32 ndarray returned by
`cv2.connectedComponents`. Each pixel holds a small integer (0 = background,
1..N = component IDs).
"""

import numpy as np

from fiatlight.fiat_types.typename_utils import documented_newtype


LabelImage = documented_newtype(
    "LabelImage",
    np.ndarray,
    "Connected-components label image as a (H, W) int32 ndarray. "
    "0 = background, 1..N = component IDs. Returned by cv2.connectedComponents.",
)
