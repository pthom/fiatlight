from fiatlight.demos.math.demo_float_functions import float_source, sin, log, square, add, mul, sub, div
from fiatlight.fiat_types import FunctionList


def all_functions() -> FunctionList:
    from fiatlight.demos.math.demo_float_functions import all_functions as all_float_functions

    return all_float_functions  # type: ignore


__all__ = [
    "all_functions",
    "float_source",
    "sin",
    "log",
    "square",
    "add",
    "mul",
    "sub",
    "div",
]
