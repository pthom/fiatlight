from fiatlight.fiat_image.image_types import (
    ImageU8,
    ImageFloat,
    Image,
    ChannelsImageU8,
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
from fiatlight.fiat_image.image_gui import ImageWithGui, ImageChannelsWithGui, ImagePresenterParams, image_source
from fiatlight.fiat_image.cv_color_type import ColorType, ColorConversion
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


def _register_factories() -> None:
    from fiatlight.fiat_image.image_types import _register_image_type_factories
    from fiatlight.fiat_core import gui_factories, composite_gui

    _register_image_type_factories()
    gui_factories().register_factory("ColorConversion", ColorConversionWithGui)
    gui_factories().register_factory("ColorType", lambda: composite_gui.EnumWithGui(ColorType))
    gui_factories().register_factory("fiatlight.fiat_image.lut.LutParams", LutParamsWithGui)


_register_factories()


__all__ = [
    # from image_types
    "ImageU8",
    "ImageFloat",
    "Image",
    "ChannelsImageU8",
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
    "image_source",
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
