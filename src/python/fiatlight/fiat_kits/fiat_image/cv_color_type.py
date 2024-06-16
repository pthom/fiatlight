from typing import List, Optional, Dict
import enum
import cv2
from typing import TypeAlias, Any
from numpy.typing import NDArray
from fiatlight.fiat_kits.fiat_image.image_types import ImageU8
from fiatlight.fiat_togui.gui_registry import base_model_with_gui_registration
from pydantic import BaseModel


CvColorConversionCode: TypeAlias = int

NO_COLOR_CONVERSION_CODE: CvColorConversionCode = -123456789


class ColorType(enum.Enum):
    """Color types for images (BGR, BGRA, RGB, RGBA, HSV, HLS, Lab, Luv, XYZ, Gray)."""

    BGR = enum.auto()
    BGRA = enum.auto()
    RGB = enum.auto()
    RGBA = enum.auto()
    HSV = enum.auto()
    HLS = enum.auto()
    Lab = enum.auto()
    Luv = enum.auto()
    XYZ = enum.auto()
    Gray = enum.auto()

    def channels_names(self) -> List[str]:
        return list(self.name)

    def channel_name(self, i: int) -> str:
        names = self.channels_names()
        assert 0 <= i < len(names)
        return names[i]

    @staticmethod
    def all_color_types() -> List["ColorType"]:
        return list(ColorType)

    def color_conversion_to_bgr(self) -> Optional["ColorConversion"]:
        conversion_code = _optional_cv_color_conversion_code_between(self, ColorType.BGR)
        if conversion_code is None:
            return None
        else:
            return ColorConversion(src_color=self, dst_color=ColorType.BGR)

    def color_conversion_from_bgr(self) -> Optional["ColorConversion"]:
        conversion_code = _optional_cv_color_conversion_code_between(ColorType.BGR, self)
        if conversion_code is None:
            return None
        else:
            return ColorConversion(src_color=ColorType.BGR, dst_color=self)

    @staticmethod
    def available_color_types_for_image(image: NDArray[Any]) -> List["ColorType"]:
        nb_channels = image.shape[-1] if len(image.shape) == 3 else 1
        if nb_channels == 1:
            return [ColorType.Gray]
        elif nb_channels == 3:
            return [
                ColorType.BGR,
                ColorType.RGB,
                ColorType.HSV,
                ColorType.HLS,
                ColorType.Lab,
                ColorType.Luv,
                ColorType.XYZ,
            ]
        elif nb_channels == 4:
            return [ColorType.BGRA, ColorType.RGBA]
        else:
            return []

    def available_conversion_outputs(self) -> List["ColorType"]:
        r = []
        for color_type2 in ColorType:
            if color_type2 != self:
                if _optional_cv_color_conversion_code_between(self, color_type2) is not None:
                    r.append(color_type2)
        return r

    def conversion_code(self, dst_color: "ColorType") -> Optional[CvColorConversionCode]:
        return _optional_cv_color_conversion_code_between(self, dst_color)


@base_model_with_gui_registration()
class ColorConversion(BaseModel):
    """A color conversion from one color space to another (color spaces use the ColorType enum)."""

    src_color: ColorType = ColorType.RGB
    dst_color: ColorType = ColorType.RGB

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.conversion_code() is None:
            raise ValueError(f"Conversion from {self.src_color} to {self.dst_color} is not available")

    def conversion_code(self) -> Optional[CvColorConversionCode]:
        return self.src_color.conversion_code(self.dst_color)

    def convert_image(self, image: ImageU8) -> ImageU8:
        conversion_code = self.conversion_code()
        if conversion_code == NO_COLOR_CONVERSION_CODE:
            return image
        assert conversion_code is not None
        return cv2.cvtColor(image, conversion_code)  # type: ignore

    def __str__(self) -> str:
        return f"{self.src_color.name}=>{self.dst_color.name}"


def color_convert(image: ImageU8, color_conversion: ColorConversion) -> ImageU8:
    return color_conversion.convert_image(image)


def _optional_cv_color_conversion_code_between(type1: ColorType, type2: ColorType) -> CvColorConversionCode | None:
    conversions: Dict[ColorType, CvColorConversionCode]
    if type1 == type2:
        return NO_COLOR_CONVERSION_CODE
    if type1 == ColorType.BGR:
        conversions = {
            ColorType.BGRA: cv2.COLOR_BGR2BGRA,
            ColorType.RGB: cv2.COLOR_BGR2RGB,
            ColorType.RGBA: cv2.COLOR_BGRA2RGBA,
            ColorType.HSV: cv2.COLOR_BGR2HSV_FULL,
            ColorType.HLS: cv2.COLOR_BGR2HLS_FULL,
            ColorType.Lab: cv2.COLOR_BGR2Lab,
            ColorType.Luv: cv2.COLOR_BGR2Luv,
            ColorType.XYZ: cv2.COLOR_BGR2XYZ,
            ColorType.Gray: cv2.COLOR_BGR2GRAY,
        }

    elif type1 == ColorType.BGRA:
        conversions = {
            ColorType.BGR: cv2.COLOR_BGRA2BGR,
            ColorType.RGB: cv2.COLOR_BGRA2RGB,
            ColorType.RGBA: cv2.COLOR_BGRA2RGBA,
            ColorType.Gray: cv2.COLOR_BGRA2GRAY,
        }

    elif type1 == ColorType.RGB:
        conversions = {
            ColorType.BGR: cv2.COLOR_RGB2BGR,
            ColorType.BGRA: cv2.COLOR_RGB2BGRA,
            ColorType.RGBA: cv2.COLOR_RGB2RGBA,
            ColorType.HSV: cv2.COLOR_RGB2HSV_FULL,
            ColorType.HLS: cv2.COLOR_RGB2HLS_FULL,
            ColorType.Lab: cv2.COLOR_RGB2Lab,
            ColorType.Luv: cv2.COLOR_RGB2Luv,
            ColorType.XYZ: cv2.COLOR_RGB2XYZ,
            ColorType.Gray: cv2.COLOR_RGB2GRAY,
        }

    elif type1 == ColorType.RGBA:
        conversions = {
            ColorType.BGR: cv2.COLOR_RGBA2BGR,
            ColorType.BGRA: cv2.COLOR_RGBA2BGRA,
            ColorType.RGB: cv2.COLOR_RGBA2RGB,
            ColorType.Gray: cv2.COLOR_RGBA2GRAY,
        }

    elif type1 == ColorType.HSV:
        conversions = {
            ColorType.BGR: cv2.COLOR_HSV2BGR_FULL,
            ColorType.RGB: cv2.COLOR_HSV2RGB_FULL,
        }

    elif type1 == ColorType.HLS:
        conversions = {
            ColorType.BGR: cv2.COLOR_HLS2BGR_FULL,
            ColorType.RGB: cv2.COLOR_HLS2RGB_FULL,
        }

    elif type1 == ColorType.Lab:
        conversions = {
            ColorType.BGR: cv2.COLOR_Lab2BGR,
            ColorType.RGB: cv2.COLOR_Lab2RGB,
        }

    elif type1 == ColorType.Luv:
        conversions = {
            ColorType.BGR: cv2.COLOR_Luv2BGR,
            ColorType.RGB: cv2.COLOR_Luv2RGB,
        }

    elif type1 == ColorType.XYZ:
        conversions = {
            ColorType.BGR: cv2.COLOR_XYZ2BGR,
            ColorType.RGB: cv2.COLOR_XYZ2RGB,
        }

    elif type1 == ColorType.Gray:
        conversions = {
            ColorType.BGR: cv2.COLOR_GRAY2BGR,
            ColorType.RGB: cv2.COLOR_GRAY2RGB,
            ColorType.BGRA: cv2.COLOR_GRAY2BGRA,
            ColorType.RGBA: cv2.COLOR_GRAY2RGBA,
        }
    else:
        conversions = {}

    if type2 in conversions:
        return conversions[type2]

    return None


def sandbox() -> None:
    def f(c: ColorType) -> None:
        pass

    import fiatlight

    fiatlight.run(f)


if __name__ == "__main__":
    sandbox()
