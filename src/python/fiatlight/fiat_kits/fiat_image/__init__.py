from .image_types import (
    ImageU8,
    ImageFloat,
    Image,
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
from .image_gui import (
    ImageWithGui,
    ImagePresenterParams,
    image_source,
)
from .cv_color_type import ColorType, ColorConversion
from .cv_color_type_gui import ColorConversionWithGui
from .lut_functions import (
    LutParams,
    LutTable,
    lut_with_params,
    lut_channels_with_params,
    lut_channels_in_colorspace,
)
from .lut_gui import LutParamsWithGui
from .overlay_alpha_image import overlay_alpha_image
from .image_to_from_file_gui import image_from_file, ImageToFileGui
from .camera_image_provider import CameraImageProvider, CameraImageProviderGui


def _register_factories() -> None:
    from .image_types import _register_image_type_factories
    from fiatlight.fiat_togui.to_gui import register_type, register_enum

    _register_image_type_factories()
    register_type(ColorConversion, ColorConversionWithGui)
    register_type(LutParams, LutParamsWithGui)
    register_enum(ColorType)


_register_factories()


__all__ = [
    # from image_types
    "ImageU8",
    "ImageFloat",
    "Image",
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
    "lut_with_params",
    "lut_channels_with_params",
    "lut_channels_in_colorspace",
    # from lut_gui
    "LutParamsWithGui",
    # from overlay_alpha_image
    "overlay_alpha_image",
    # from image_to_from_file_gui
    "image_from_file",
    "ImageToFileGui",
    # from camera_image_provider
    "CameraImageProvider",
    "CameraImageProviderGui",
]
