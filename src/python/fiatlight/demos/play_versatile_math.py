from fiatlight import FunctionsGraph, fiat_run
import math


def main() -> None:
    def float_source(x: float) -> float:
        """A source where you can specify an input value."""
        return x

    def sin(x: float) -> float:
        """A function that computes the sine of its input."""
        return math.sin(x)

    def log(x: float) -> float:
        """A function that computes the natural logarithm of its input.
        Works only for positive inputs!
        """
        return math.log(x)

    def add_mul(a: float, b: float) -> tuple[float, float]:
        """An example of a function that returns multiple values."""
        return a + b, a * b

    functions_graph = FunctionsGraph.from_function_composition([float_source, sin, add_mul, log, sin])
    functions_graph.add_function_composition([float_source, sin, log, sin, add_mul])

    fiat_run(functions_graph)


if __name__ == "__main__":
    main()
