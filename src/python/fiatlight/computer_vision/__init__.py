from fiatlight.computer_vision.image_types import ImageUInt8, ImageFloat, Image, ImageUInt8Channels
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

    gui_factories().add_factory("ImageUInt8", ImageWithGui)
    gui_factories().add_factory("ImageUInt8Channels", ImageChannelsWithGui)
    gui_factories().add_factory("numpy.ndarray[typing.Any, numpy.dtype[numpy.uint8]]", ImageWithGui)

    gui_factories().add_factory("ColorConversion", ColorConversionWithGui)
    gui_factories().add_factory("ColorType", lambda: composite_gui.EnumWithGui(ColorType))
    gui_factories().add_factory("fiatlight.computer_vision.lut.LutParams", LutParamsWithGui)


register_gui_factories()


__all__ = [
    # from image_types
    "ImageUInt8",
    "ImageFloat",
    "Image",
    "ImageUInt8Channels",
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
