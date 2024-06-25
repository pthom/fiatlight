"""In this example, validate_missing_return does not return a string as expected by the validator signature.
We should display a nice exception that mentions the location of the validator.
"""
import fiatlight as fl


def validate_missing_return(value: int) -> None:
    pass


@fl.with_fiat_attributes(value__validator=validate_missing_return)
def f(value: int) -> int:
    return value


fl.run(f)
