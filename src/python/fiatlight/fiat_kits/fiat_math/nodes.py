"""Math node functions (category `math`, applied by the kit defaults).

Plain functions over built-in numeric types; the type->GUI registry renders the
int/float/list widgets automatically. Names avoid shadowing builtins (e.g.
`power`, `absolute`, `total`, `minimum`) so ruff stays happy and the bodies can
still call the builtins.
"""
import math

from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes


# ----------------------------------------------------------------------------- source
@with_fiat_attributes(x__edit_type="slider_float_any_range", fiat_tags=["source"])
def float_source(x: float = 0.0) -> float:
    """A source node: set a float value to feed downstream nodes."""
    return x


# ----------------------------------------------------------------------------- arithmetic
@with_fiat_attributes(fiat_tags=["arithmetic"])
def add(a: float = 0.0, b: float = 0.0) -> float:
    return a + b


@with_fiat_attributes(fiat_tags=["arithmetic"])
def sub(a: float = 0.0, b: float = 0.0) -> float:
    return a - b


@with_fiat_attributes(fiat_tags=["arithmetic"])
def mul(a: float = 1.0, b: float = 1.0) -> float:
    return a * b


@with_fiat_attributes(fiat_tags=["arithmetic"])
def div(a: float = 0.0, b: float = 1.0) -> float:
    return a / b


@with_fiat_attributes(fiat_tags=["arithmetic"])
def modulo(a: float = 0.0, b: float = 1.0) -> float:
    return a % b


@with_fiat_attributes(fiat_tags=["arithmetic"])
def square(x: float = 0.0) -> float:
    return x * x


@with_fiat_attributes(fiat_tags=["arithmetic"])
def power(base: float = 1.0, exponent: float = 2.0) -> float:
    return float(base**exponent)


@with_fiat_attributes(fiat_tags=["arithmetic"])
def absolute(x: float = 0.0) -> float:
    return abs(x)


# ----------------------------------------------------------------------------- int arithmetic
# Same operations over `int`, so the GUI renders integer (not float) widgets and the
# results stay integers (e.g. `int_div` is floor division).
@with_fiat_attributes(fiat_tags=["source"])
def int_source(x: int = 0) -> int:
    """A source node: set an int value to feed downstream nodes."""
    return x


@with_fiat_attributes(fiat_tags=["int"])
def int_add(a: int = 0, b: int = 0) -> int:
    return a + b


@with_fiat_attributes(fiat_tags=["int"])
def int_sub(a: int = 0, b: int = 0) -> int:
    return a - b


@with_fiat_attributes(fiat_tags=["int"])
def int_mul(a: int = 1, b: int = 1) -> int:
    return a * b


@with_fiat_attributes(fiat_tags=["int"])
def int_div(a: int = 0, b: int = 1) -> int:
    """Integer (floor) division."""
    return a // b


@with_fiat_attributes(fiat_tags=["int"])
def int_mod(a: int = 0, b: int = 1) -> int:
    return a % b


@with_fiat_attributes(fiat_tags=["int"])
def int_power(base: int = 1, exponent: int = 2) -> int:
    return int(base**exponent)


@with_fiat_attributes(fiat_tags=["int"])
def int_abs(x: int = 0) -> int:
    return abs(x)


# ----------------------------------------------------------------------------- scalar / transcendental
@with_fiat_attributes(fiat_tags=["trig"])
def sin(x: float = 0.0) -> float:
    return math.sin(x)


@with_fiat_attributes(fiat_tags=["trig"])
def cos(x: float = 0.0) -> float:
    return math.cos(x)


@with_fiat_attributes(fiat_tags=["trig"])
def tan(x: float = 0.0) -> float:
    return math.tan(x)


@with_fiat_attributes(fiat_tags=["scalar"])
def log(x: float = 1.0) -> float:
    """Natural logarithm (defined for x > 0)."""
    return math.log(x)


@with_fiat_attributes(fiat_tags=["scalar"])
def exp(x: float = 0.0) -> float:
    return math.exp(x)


@with_fiat_attributes(fiat_tags=["scalar"])
def sqrt(x: float = 0.0) -> float:
    """Square root (defined for x >= 0)."""
    return math.sqrt(x)


# ----------------------------------------------------------------------------- rounding
@with_fiat_attributes(fiat_tags=["round"])
def floor(x: float = 0.0) -> int:
    return math.floor(x)


@with_fiat_attributes(fiat_tags=["round"])
def ceil(x: float = 0.0) -> int:
    return math.ceil(x)


@with_fiat_attributes(fiat_tags=["round"])
def round_value(x: float = 0.0) -> int:
    return round(x)


# ----------------------------------------------------------------------------- reduce (list -> scalar)
# These take a `list[float]` and so only fire when fed from a link (list inputs
# are not hand-editable). They bridge list-producing nodes into scalar math.
@with_fiat_attributes(fiat_tags=["reduce"])
def total(values: list[float]) -> float:
    return sum(values)


@with_fiat_attributes(fiat_tags=["reduce"])
def average(values: list[float]) -> float:
    return sum(values) / len(values)


@with_fiat_attributes(fiat_tags=["reduce"])
def minimum(values: list[float]) -> float:
    return min(values)


@with_fiat_attributes(fiat_tags=["reduce"])
def maximum(values: list[float]) -> float:
    return max(values)


@with_fiat_attributes(fiat_tags=["reduce"])
def count_values(values: list[float]) -> int:
    return len(values)
