from fiatlight.fiat_image.image_types import (
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
from fiatlight.fiat_image import fiat_img_proc
from fiatlight.fiat_image.image_gui import ImageWithGui, ImageChannelsWithGui, ImagePresenterParams
from fiatlight.fiat_image.cv_color_type import ColorConversion, ColorType
from fiatlight.fiat_image.cv_color_type_gui import ColorConversionWithGui
from fiatlight.fiat_image.lut import (
    LutParams,
    LutTable,
    lut,
    lut_with_params,
    lut_channels_with_params,
    lut_channels_in_colorspace,
)
from fiatlight.fiat_image.lut_gui import LutParamsWithGui
from fiatlight.fiat_core import composite_gui


def register_gui_factories() -> None:
    from fiatlight.fiat_core import gui_factories

    gui_factories().add_factory("ImageU8", ImageWithGui)
    gui_factories().add_factory("ImageU8Channels", ImageChannelsWithGui)
    gui_factories().add_factory("numpy.ndarray[typing.Any, numpy.dtype[numpy.uint8]]", ImageWithGui)

    gui_factories().add_factory("ColorConversion", ColorConversionWithGui)
    gui_factories().add_factory("ColorType", lambda: composite_gui.EnumWithGui(ColorType))
    gui_factories().add_factory("fiatlight.fiat_image.lut.LutParams", LutParamsWithGui)


register_gui_factories()


__all__ = [
    # submodules
    "fiat_img_proc",
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
