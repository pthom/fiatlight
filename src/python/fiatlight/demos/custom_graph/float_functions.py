import math
from fiatlight.fiat_core import FunctionWithGuiFactory, to_function_with_gui_factory
from fiatlight.fiat_types import Function
from typing import List


def float_source(x: float) -> float:
    return x


def add(a: float, b: float) -> float:
    return a + b


def mul(a: float, b: float) -> float:
    return a * b


def sub(a: float, b: float) -> float:
    return a - b


def div(a: float, b: float) -> float:
    return a / b


def log(x: float) -> float:
    return math.log(x)


def all_functions() -> List[FunctionWithGuiFactory]:
    fn_list: List[Function] = [add, mul, sub, div, log, float_source]
    return [to_function_with_gui_factory(f) for f in fn_list]
