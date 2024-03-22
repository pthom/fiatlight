from typing import TypeAlias, Any, NewType
import numpy as np
from numpy.typing import NDArray


ImageUInt8: TypeAlias = NDArray[np.uint8]
ImageFloat: TypeAlias = NDArray[np.floating[Any]]
Image: TypeAlias = NDArray[np.uint8 | np.floating[Any]]

# ImageUInt8Channels is a synonym for ImageUInt8, used when we want to
# display the channels of an image as separate images (in the GUI).
# (beside the difference in the name, the two types are identical)
ImageUInt8Channels = NewType("ImageUInt8Channels", ImageUInt8)
