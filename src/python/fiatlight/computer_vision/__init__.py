from fiatlight.computer_vision.image_types import (
    ImageU8,
    ImageFloat,
    Image,
    ImageU8Channels,
    ImageU8_RGB,
    ImageU8_RGBA,
    ImageU8_BGRA,
    ImageU8_BGR,
    ImageU8_GRAY,
    ImageU8_1,
    ImageU8_2,
    ImageU8_3,
    ImageU8_4,
)
from fiatlight.computer_vision.image_gui import ImageWithGui, ImageChannelsWithGui, ImagePresenterParams
from fiatlight.computer_vision.cv_color_type import ColorConversion, ColorType
from fiatlight.computer_vision.cv_color_type_gui import ColorConversionWithGui
from fiatlight.computer_vision.lut import (
    LutParams,
    LutTable,
    lut,
    lut_with_params,
    lut_channels_with_params,
    lut_channels_in_colorspace,
)
from fiatlight.computer_vision.lut_gui import LutParamsWithGui
from fiatlight.core import composite_gui


def register_gui_factories() -> None:
    from fiatlight.core import gui_factories

    gui_factories().add_factory("ImageU8", ImageWithGui)
    gui_factories().add_factory("ImageU8Channels", ImageChannelsWithGui)
    gui_factories().add_factory("numpy.ndarray[typing.Any, numpy.dtype[numpy.uint8]]", ImageWithGui)

    gui_factories().add_factory("ColorConversion", ColorConversionWithGui)
    gui_factories().add_factory("ColorType", lambda: composite_gui.EnumWithGui(ColorType))
    gui_factories().add_factory("fiatlight.computer_vision.lut.LutParams", LutParamsWithGui)


register_gui_factories()


__all__ = [
    # from image_types
    "ImageU8",
    "ImageFloat",
    "Image",
    "ImageU8Channels",
    "ImageU8_RGB",
    "ImageU8_RGBA",
    "ImageU8_BGRA",
    "ImageU8_BGR",
    "ImageU8_GRAY",
    "ImageU8_1",
    "ImageU8_2",
    "ImageU8_3",
    "ImageU8_4",
    # from image_gui
    "ImageWithGui",
    "ImageChannelsWithGui",
    "ImagePresenterParams",
    # from cv_color_type
    "ColorConversion",
    "ColorType",
    # from cv_color_type_gui
    "ColorConversionWithGui",
    # from lut
    "LutParams",
    "LutTable",
    "lut",
    "lut_with_params",
    "lut_channels_with_params",
    "lut_channels_in_colorspace",
    # from lut_gui
    "LutParamsWithGui",
]
