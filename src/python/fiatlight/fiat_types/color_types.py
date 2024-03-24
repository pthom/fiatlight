from typing import NewType, Tuple

ColorRgb = NewType("ColorRgb", Tuple[int, int, int])
ColorRgba = NewType("ColorRgba", Tuple[int, int, int, int])


# from collections import namedtuple
#
# ColorRgb = namedtuple("ColorRgb", ["red", "green", "blue"])
# ColorRgba = namedtuple("ColorRgba", ["red", "green", "blue", "alpha"])
