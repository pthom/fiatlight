"""Math node pack for fiatlight.

A small batteries-included set of math functions over built-in numeric types,
each tagged by intent and put in the `math` category (applied once by the kit
defaults). `math_nodes()` returns them in a stable order.
"""
from typing import Callable, List, Any

from fiatlight.fiat_utils.fiat_attributes_decorator import add_fiat_attributes
from .nodes import (
    float_source,
    add,
    sub,
    mul,
    div,
    modulo,
    square,
    power,
    absolute,
    sin,
    cos,
    tan,
    log,
    exp,
    sqrt,
    floor,
    ceil,
    round_value,
    total,
    average,
    minimum,
    maximum,
    count_values,
)

__all__ = [
    "math_nodes",
    "float_source",
    "add",
    "sub",
    "mul",
    "div",
    "modulo",
    "square",
    "power",
    "absolute",
    "sin",
    "cos",
    "tan",
    "log",
    "exp",
    "sqrt",
    "floor",
    "ceil",
    "round_value",
    "total",
    "average",
    "minimum",
    "maximum",
    "count_values",
]


def math_nodes() -> List[Callable[..., Any]]:
    """Return every math node, grouped by intent (stable order)."""
    return [
        # source
        float_source,
        # arithmetic
        add,
        sub,
        mul,
        div,
        modulo,
        square,
        power,
        absolute,
        # scalar / transcendental
        sin,
        cos,
        tan,
        log,
        exp,
        sqrt,
        # rounding
        floor,
        ceil,
        round_value,
        # reduce (list -> scalar)
        total,
        average,
        minimum,
        maximum,
        count_values,
    ]


def _apply_kit_defaults() -> None:
    """Put every node in this pack in the `math` category, once, instead of
    repeating `fiat_category="math"` on each function."""
    for fn in math_nodes():
        add_fiat_attributes(fn, fiat_category="math")


_apply_kit_defaults()
