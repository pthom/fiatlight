import fiatlight as fl


def validate_missing_return(value: int) -> None:
    if value % 2 != 1:
        raise ValueError("must be an odd number")


@fl.with_fiat_attributes(value__validate_value=validate_missing_return)
def f(value: int) -> int:
    return value


fl.run(f)
