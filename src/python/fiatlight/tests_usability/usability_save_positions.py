import fiatlight as fl
import math


def cos(x: float) -> float:
    return math.cos(math.radians(x))


def sin(x: float) -> float:
    return math.sin(math.radians(x))


def float_source(x: float) -> float:
    return x


fl.run([float_source, cos, sin], app_name="_save_pos")
