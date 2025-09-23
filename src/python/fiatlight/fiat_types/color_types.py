from typing import NewType
from imgui_bundle import ImVec4


ColorRgb = NewType("ColorRgb", tuple[int, int, int])
ColorRgb.__doc__ = "synonym for tuple[int, int, int] describing an RGB color, with values in [0, 255] (NewType)"

ColorRgba = NewType("ColorRgba", tuple[int, int, int, int])
ColorRgba.__doc__ = "synonym for tuple[int, int, int, int] describing an RGBA color, with values in [0, 255] (NewType)"

ColorRgbFloat = NewType("ColorRgbFloat", tuple[float, float, float])
ColorRgbFloat.__doc__ = (
    "synonym for tuple[float, float, float] describing an RGB color, with values in [0, 1] (NewType)"
)

ColorRgbaFloat = NewType("ColorRgbaFloat", tuple[float, float, float, float])
ColorRgbaFloat.__doc__ = (
    "synonym for tuple[float, float, float, float] describing an RGBA color, with values in [0, 1] (NewType)"
)


def _int255_to_float(value: int) -> float:
    return value / 255.0


def _float_to_int255(value: float) -> int:
    return int(value * 255)


def color_rgb_to_color_rgb_float(color_rgb: ColorRgb) -> ColorRgbFloat:
    return ColorRgbFloat(tuple(_int255_to_float(value) for value in color_rgb))  # type: ignore


def color_rgba_to_color_rgba_float(color_rgba: ColorRgba) -> ColorRgbaFloat:
    return ColorRgbaFloat(tuple(_int255_to_float(value) for value in color_rgba))  # type: ignore


def color_rgb_float_to_color_rgb(color_rgb_float: ColorRgbFloat) -> ColorRgb:
    return ColorRgb(tuple(_float_to_int255(value) for value in color_rgb_float))  # type: ignore


def color_rgba_float_to_color_rgba(color_rgba_float: ColorRgbaFloat) -> ColorRgba:
    return ColorRgba(tuple(_float_to_int255(value) for value in color_rgba_float))  # type: ignore


def color_rgb_to_color_rgba(color_rgb: ColorRgb) -> ColorRgba:
    return ColorRgba(color_rgb + (255,))


def color_rgb_float_to_color_rgba_float(color_rgb_float: ColorRgbFloat) -> ColorRgbaFloat:
    return ColorRgbaFloat(color_rgb_float + (1.0,))


def color_rgb_to_imvec4(v: ColorRgb) -> ImVec4:
    return ImVec4(v[0] / 255.0, v[1] / 255.0, v[2] / 255.0, 1.0)


def color_rgba_to_imvec4(v: ColorRgba) -> ImVec4:
    return ImVec4(v[0] / 255.0, v[1] / 255.0, v[2] / 255.0, v[3] / 255.0)


def color_rgb_float_to_imvec4(v: ColorRgbFloat) -> ImVec4:
    return ImVec4(v[0], v[1], v[2], 1.0)


def color_rgba_float_to_imvec4(v: ColorRgbaFloat) -> ImVec4:
    return ImVec4(v[0], v[1], v[2], v[3])
