from fiatlux.computer_vision.image_with_gui import ImageWithGui, ImageChannelsWithGui
from typing import Any
from numpy.typing import NDArray
import numpy as np

ImageUInt8 = NDArray[np.uint8]
ImageFloat = NDArray[np.floating[Any]]


__all__ = [
    "ImageUInt8",
    "ImageFloat",
    "ImageWithGui",
    "ImageChannelsWithGui",
]
