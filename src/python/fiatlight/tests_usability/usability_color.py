import fiatlight as fl
from fiatlight.fiat_types import ColorRgbaFloat, ColorRgbFloat, ColorRgb, ColorRgba


def f(
    c3f: ColorRgbFloat, c4f: ColorRgbaFloat, c3: ColorRgb, c4: ColorRgba
) -> tuple[ColorRgbFloat, ColorRgbaFloat, ColorRgb, ColorRgba]:
    return c3f, c4f, c3, c4


fl.run(f)
