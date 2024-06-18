import fiatlight as fl


def validate_odd_int(odd_int: int) -> None:
    if odd_int % 2 != 1:
        raise ValueError("must be an odd number")


@fl.with_fiat_attributes(odd_int__range=(0, 6), odd_int__validate_value=validate_odd_int)
def f(odd_int: int) -> int:
    return odd_int + 1


fl.run(f)
