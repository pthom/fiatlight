from .image_types import (
    ImageU8,
    ImageFloat,
    Image,
    ImageRgb,
    ImageRgba,
    ImageBgra,
    ImageBgr,
    ImageU8_GRAY,
    ImageU8_1,
    ImageU8_2,
    ImageU8_3,
    ImageU8_4,
)
from .image_gui import ImageWithGui, ImagePresenterParams, image_source
from .overlay_alpha_image import overlay_alpha_image
from .image_to_from_file_gui import image_from_file, ImageToFileGui
from .contours_types import Contours, ContoursHierarchy
from .contours_gui import ContoursWithGui, ContoursHierarchyWithGui
from .points2d_types import Points2D
from .points2d_gui import Points2DWithGui

# Most of the features of fiatlight.fiat_image require OpenCV
try:
    HAS_OPENCV = True
    from .cv_color_type import ColorType, ColorConversion
    from .lut_functions import (
        lut_with_params,
        lut_channels_with_params,
        lut_channels_in_colorspace,
    )
    from .lut_types import LutParams, LutTable
    from .lut_gui import LutParamsWithGui
    from .camera_image_provider import CameraImageProvider, CameraImageProviderGui
    from .imread_rgb import imread_rgb
except ImportError:
    HAS_OPENCV = False
    pass


def _register_factories() -> None:
    from .image_types import _register_image_type_factories
    from fiatlight.fiat_togui.gui_registry import register_type, register_typing_new_type

    _register_image_type_factories()
    register_typing_new_type(Contours, ContoursWithGui)
    register_typing_new_type(ContoursHierarchy, ContoursHierarchyWithGui)
    register_typing_new_type(Points2D, Points2DWithGui)
    if HAS_OPENCV:
        register_type(LutParams, LutParamsWithGui)


_register_factories()

_was_color_order_registered = False
if not _was_color_order_registered:
    from imgui_bundle import immvision

    immvision.use_rgb_color_order()


__all__ = [
    # from image_types
    "ImageU8",
    "ImageFloat",
    "Image",
    "ImageRgb",
    "ImageRgba",
    "ImageBgra",
    "ImageBgr",
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
    # "ColorConversionWithGui",
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
    # from imread_rgb
    "imread_rgb",
    # from contours_types / contours_gui
    "Contours",
    "ContoursHierarchy",
    "ContoursWithGui",
    "ContoursHierarchyWithGui",
    # from points2d_types / points2d_gui
    "Points2D",
    "Points2DWithGui",
]
