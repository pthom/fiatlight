import math


def square(x: float) -> float:
    """A function that computes the square of its input."""
    return x * x


def add(a: float, b: float) -> float:
    return a + b


def mul(a: float, b: float) -> float:
    return a * b


def sub(a: float, b: float) -> float:
    return a - b


def div(a: float, b: float) -> float:
    return a / b


def sin(x: float) -> float:
    """A function that computes the sine of its input."""
    return math.sin(x)


def log(x: float) -> float:
    """A function that computes the natural logarithm of its input.
    Works only for positive inputs!
    """
    return math.log(x)


def float_source(x: float) -> float:
    """A source where you can specify an input value."""
    return x


float_source.x__edit_type = "slider_float_any_range"  # type: ignore


def sandbox() -> None:
    import fiatlight as fl

    fl.run([float_source, sin, log], app_name="sandbox_float_functions")


def manual_sandbox() -> None:
    x = 0
    z = sin(x)
    w = log(z)
    print(w)


if __name__ == "__main__":
    sandbox()
    # manual_sandbox()


all_functions = [
    float_source,
    sin,
    log,
    square,
    add,
    mul,
    sub,
    div,
]
