from typing import NewType

ColorRgb = NewType("ColorRgb", tuple[int, int, int])
ColorRgba = NewType("ColorRgba", tuple[int, int, int, int])
ColorRgbFloat = NewType("ColorRgbFloat", tuple[float, float, float])
ColorRgbaFloat = NewType("ColorRgbaFloat", tuple[float, float, float, float])


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
