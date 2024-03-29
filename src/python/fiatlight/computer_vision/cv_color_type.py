from typing import List, Optional, Dict
import enum
import cv2
from typing import TypeAlias, Any
from numpy.typing import NDArray


CvColorConversionCode: TypeAlias = int


class ColorType(enum.Enum):
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
            return ColorConversion(self, ColorType.BGR)

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


class ColorConversion:
    src_color: ColorType
    dst_color: ColorType

    def __init__(self, src_color: ColorType, dst_color: ColorType) -> None:
        self.src_color = src_color
        self.dst_color = dst_color

    def conversion_code(self) -> Optional[CvColorConversionCode]:
        return self.src_color.conversion_code(self.dst_color)

    def convert_image(self, image: NDArray[Any]) -> Optional[NDArray[Any]]:
        conversion_code = self.conversion_code()
        assert conversion_code is not None
        return cv2.cvtColor(image, conversion_code)

    def __str__(self) -> str:
        return f"{self.src_color.name}=>{self.dst_color.name}"

    @staticmethod
    def make_default_color_conversion(image: NDArray[Any]) -> "OptionalColorConversion":
        available_src_colors = ColorType.available_color_types_for_image(image)
        if len(available_src_colors) == 0:
            return None
        src_color = available_src_colors[0]
        available_dst_colors = src_color.available_conversion_outputs()
        if len(available_dst_colors) == 0:
            return None
        dst_color = available_dst_colors[0]
        return ColorConversion(src_color, dst_color)


OptionalColorConversion: TypeAlias = Optional[ColorConversion]


def _optional_cv_color_conversion_code_between(type1: ColorType, type2: ColorType) -> Optional[CvColorConversionCode]:
    conversions: Dict[ColorType, CvColorConversionCode]
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


# @dataclass
# class OldColorConversion:
#     name: str
#     src_color: ColorType
#     dst_color: ColorType
#     conversion_code: CvColorConversionCode
#
#
# @dataclass
# class OldColorConversionPair:
#     """Two inverse color conversions"""
#
#     name: str
#     conversion: OldColorConversion
#     inv_conversion: OldColorConversion
#


# def compute_possible_conversion_pairs(color_type: ColorType) -> List[OldColorConversionPair]:
#     r: List[OldColorConversionPair] = []
#     for other_color_type in ColorType:
#         conversion_code = cv_color_conversion_code_between(color_type, other_color_type)
#         conversion_code_inv = cv_color_conversion_code_between(other_color_type, color_type)
#         if conversion_code is not None and conversion_code_inv is not None:
#             conversion_direct = OldColorConversion(
#                 f"{color_type.name}=>{other_color_type.name}", color_type, other_color_type, conversion_code
#             )
#             conversion_inv = OldColorConversion(
#                 f"{other_color_type.name}=>{color_type.name}", other_color_type, color_type, conversion_code_inv
#             )
#             conversion_pair = OldColorConversionPair(
#                 f"{color_type.name}=>{other_color_type.name}=>{color_type.name}", conversion_direct, conversion_inv
#             )
#             r.append(conversion_pair)
#     return r
