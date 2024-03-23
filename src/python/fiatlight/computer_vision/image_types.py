from typing import TypeAlias, Any, NewType
import numpy as np
from numpy.typing import NDArray


# Type aliases for image types:
Image: TypeAlias = NDArray[np.uint8 | np.floating[Any]]

# ImageU8 is the most common image type, with 8-bit unsigned integer values.
# It can have any number of channels.
ImageU8: TypeAlias = NDArray[np.uint8]

# ImageFloat is an image type with floating point values.
# It can have any number of channels.
ImageFloat: TypeAlias = NDArray[np.floating[Any]]


# ImageU8_RGB, ImageU8_RGBA, ImageU8_BGRA, ImageU8_BGR, ImageU8_GRAY are used to
# help understand the number and roles of channels in the image.
ImageU8_RGB: TypeAlias = NDArray[np.uint8]
ImageU8_RGBA: TypeAlias = NDArray[np.uint8]
ImageU8_BGRA: TypeAlias = NDArray[np.uint8]
ImageU8_BGR: TypeAlias = NDArray[np.uint8]
ImageU8_GRAY: TypeAlias = NDArray[np.uint8]

# ImageU8_1, ImageU8_2, ImageU8_3, ImageU8_4 are used to help understand the number of channels in the image.
ImageU8_1: TypeAlias = NDArray[np.uint8]  # 1 channel
ImageU8_2: TypeAlias = NDArray[np.uint8]  # 2 channels
ImageU8_3: TypeAlias = NDArray[np.uint8]  # 3 channels
ImageU8_4: TypeAlias = NDArray[np.uint8]  # 4 channels


# ImageU8Channels is a synonym for ImageU8, used when we want to
# display the channels of an image as separate images (in the GUI).
# (beside the difference in the name, the two types are identical)
ImageU8Channels = NewType("ImageU8Channels", ImageU8)
