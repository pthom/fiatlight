"""demonstrates a validator that will modify the value
In this example, it will pick the closest multiple of 6 to the input value
"""
import fiatlight as fl


def pick_closest_multiple_of_6(x: int) -> int:
    return 6 * round(x / 6)


@fl.with_fiat_attributes(
    value__range=(0, 100),
    value__validator=pick_closest_multiple_of_6,
)
def f(value: int) -> int:
    return value


fl.run(f)
