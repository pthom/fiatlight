from typing import NamedTuple
import fiatlight as fl


@fl.with_fiat_attributes(return__label="Sum", return_1__label="Product")
def calc_tuple(a: int, b: int) -> tuple[int, int]:
    return a + b, a * b


class CalcResult(NamedTuple):
    sum: int
    product: int


def calc_named_tuple(a: int, b: int) -> CalcResult:
    return CalcResult(sum=a + b, product=a * b)


graph = fl.FunctionsGraph()
graph.add_function(calc_tuple)
graph.add_function(calc_named_tuple)
fl.run(graph)
