"""This module defines several types you can use to annotate your functions.
The image types are defined as NewType instances, which are just aliases for numpy arrays.
("NewType" types are not enforced at runtime, but they are used for type checking.)

All those types will be displayed in the GUI as images, using the ImmVision image viewer
(https://github.com/pthom/immvision)

Notes:
    - The easiest way to display an image is to use the `Image` type, which is a union of all image types,
      or to use the `ImageU8` type, which is a union of all UInt8 image types.
    - any numpy array can be used to create an `Image`, and the viewer will try to display it
"""

from typing import Any, NewType
import numpy as np
from typing import Tuple, Union

# Define shape types for clarity
ShapeHeightWidth = Tuple[int, int]
ShapeHeightWidthChannels = Tuple[int, int, int]

# Define UInt8 as a dtype for numpy arrays
UInt8 = np.dtype[np.uint8]
AnyFloat = np.dtype[np.floating[Any]]


#
# UInt8 Images
#
# ImageU8 = NewType("ImageU8", np.ndarray[ShapeHeightWidthChannels | ShapeHeightWidth, UInt8])
# Type definitions for UInt8 images based on channel count
ImageU8_1 = NewType("ImageU8_1", np.ndarray[ShapeHeightWidth, UInt8])
ImageU8_2 = NewType("ImageU8_2", np.ndarray[ShapeHeightWidthChannels, UInt8])
ImageU8_3 = NewType("ImageU8_3", np.ndarray[ShapeHeightWidthChannels, UInt8])
ImageU8_4 = NewType("ImageU8_4", np.ndarray[ShapeHeightWidthChannels, UInt8])
ImageU8_WithNbChannels = Union[ImageU8_1, ImageU8_2, ImageU8_3, ImageU8_4]

# Type definitions based on the roles of the channels
ImageRgb = NewType("ImageRgb", ImageU8_3)
ImageRgba = NewType("ImageRgba", ImageU8_4)
ImageBgra = NewType("ImageBgra", ImageU8_4)
ImageBgr = NewType("ImageBgr", ImageU8_3)
ImageU8_GRAY = NewType("ImageU8_GRAY", ImageU8_1)
ImageU8_WithChannelsRoles = Union[ImageRgb, ImageRgba, ImageBgra, ImageBgr, ImageU8_GRAY]

# Generic type for any 8-bit image
ImageU8 = Union[ImageU8_WithNbChannels, ImageU8_WithChannelsRoles]


#
# Float Images
#
# Type definitions for float images based on channel count
ImageFloat_1 = NewType("ImageFloat_1", np.ndarray[ShapeHeightWidth, AnyFloat])
ImageFloat_2 = NewType("ImageFloat_2", np.ndarray[ShapeHeightWidthChannels, AnyFloat])
ImageFloat_3 = NewType("ImageFloat_3", np.ndarray[ShapeHeightWidthChannels, AnyFloat])
ImageFloat_4 = NewType("ImageFloat_4", np.ndarray[ShapeHeightWidthChannels, AnyFloat])

# Generic type for any float image
ImageFloat = Union[ImageFloat_1, ImageFloat_2, ImageFloat_3, ImageFloat_4]


#
# Generic Image Type
#
# Image is a union of all image types
Image = Union[ImageU8, ImageFloat]


# ---------------------------- Register image type factories ----------------------------


def _register_image_type_factories() -> None:
    from fiatlight.fiat_togui.gui_registry import gui_factories
    from fiatlight.fiat_kits.fiat_image.image_gui import ImageWithGui

    prefix = "fiatlight.fiat_kits.fiat_image.image_types.Image"
    gui_factories().register_factory_name_start_with(prefix, ImageWithGui)
    gui_factories().register_factory_union(prefix, ImageWithGui)
