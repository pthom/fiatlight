from fiatlight.fiat_kits.fiat_math import math_nodes, add, div, total, average, minimum, count_values
from fiatlight.fiat_palette import FunctionPalette


def test_math_pack_is_categorized_and_builds() -> None:
    p = FunctionPalette()
    for f in math_nodes():
        p.add_function(f)
    assert len(p._functions) == len(math_nodes())
    assert {fi.category for fi in p._functions} == {"math"}


def test_math_functions_compute() -> None:
    assert add(2.0, 3.0) == 5.0
    assert div(6.0, 2.0) == 3.0
    assert total([1.0, 2.0, 3.0]) == 6.0
    assert average([2.0, 4.0]) == 3.0
    assert minimum([3.0, 1.0, 2.0]) == 1.0
    assert count_values([1.0, 2.0, 3.0]) == 3
