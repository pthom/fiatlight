"""In this example we should display an error message if the user tries to set an even number to the odd_int parameter.
"""

import fiatlight as fl


def validate_odd_int(value: int) -> int:
    if value % 2 != 1:
        raise ValueError("must be an odd number")
    return value


@fl.with_fiat_attributes(odd_int__range=(0, 6), odd_int__validator=validate_odd_int)
def f(odd_int: int) -> int:
    return odd_int + 1


fl.run(f)
