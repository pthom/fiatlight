import fiatlight as fl


def validate_odd_int(value: int) -> int:
    if value % 2 != 1:
        raise ValueError("must be an odd number")
    return value


@fl.with_fiat_attributes(odd_int__range=(0, 6), odd_int__validate_value=validate_odd_int)
def f(odd_int: int) -> int:
    return odd_int + 1


fl.run(f)
