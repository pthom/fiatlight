import math
import fiatlight as fl


def my_sin(x: float) -> float:
    return math.sin(x)


@fl.with_fiat_attributes(x__range=(-10, 10))
def float_source(x: float) -> float:
    return x


graph = fl.FunctionsGraph()
fl.FunctionWithGui(my_sin)
graph.add_function_composition([float_source, my_sin, fl.FunctionWithGui(my_sin, "my_sin##2")])
fl.run(graph)
