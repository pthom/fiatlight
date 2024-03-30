import math


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


def square(x: float) -> float:
    """A function that computes the square of its input."""
    return x * x


def add_mul(a: float, b: float) -> tuple[float, float]:
    """An example of a function that returns multiple values:
    the sum and the product of its inputs.
    """
    return a + b, a * b


def main() -> None:
    from fiatlight import fiat_run_composition

    fiat_run_composition([float_source, sin, log, sin, add_mul])


if __name__ == "__main__":
    main()
