import fiatlight as fl


@fl.with_fiat_attributes(
    # customization for param x
    x__range=(0, 10),
    x__label="Value of X",
    # customization for param y
    x__edit_type="knob",
    y__range=(0, 1_000_000),
    y_label="Value of Y",
    # customization for the return value
)
def add(x: int, y: int) -> int:
    return x + y
