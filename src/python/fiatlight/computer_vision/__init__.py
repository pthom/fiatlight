from fiatlight.computer_vision.image_types import ImageUInt8, ImageFloat, Image, ImageUInt8Channels
from fiatlight.computer_vision.image_gui import ImageWithGui, ImageChannelsWithGui, ImagePresenterParams
from fiatlight.computer_vision.cv_color_type import ColorConversion, ColorType
from fiatlight.computer_vision.cv_color_type_gui import ColorConversionWithGui
from fiatlight.computer_vision.lut import LutParams, LutTable, lut, lut_with_params, lut_channels_with_params
from fiatlight.computer_vision.lut_gui import LutParamsWithGui


def register_gui_factories() -> None:
    from fiatlight.core import ALL_GUI_FACTORIES

    ALL_GUI_FACTORIES["ImageUInt8"] = ImageWithGui
    ALL_GUI_FACTORIES["ImageUInt8Channels"] = ImageChannelsWithGui
    ALL_GUI_FACTORIES["numpy.ndarray[typing.Any, numpy.dtype[numpy.uint8]]"] = ImageWithGui

    ALL_GUI_FACTORIES["fiatlight.computer_vision.ColorConversion"] = ColorConversionWithGui
    ALL_GUI_FACTORIES["ColorConversion"] = ColorConversionWithGui
    ALL_GUI_FACTORIES["fiatlight.computer_vision.lut.LutParams"] = LutParamsWithGui
    ALL_GUI_FACTORIES["LutParams"] = LutParamsWithGui


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
    # from lut_gui
    "LutParamsWithGui",
]
