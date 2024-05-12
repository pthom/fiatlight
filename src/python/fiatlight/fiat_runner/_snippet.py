import fiatlight


def to_fahrenheit(celsius: int = 10, flag: bool = False) -> float:
    return celsius * 9 / 5 + 32


to_fahrenheit.celsius__range = (-20, 60)  # type: ignore
to_fahrenheit.celsius__edit_type = "slider_and_minus_plus"  # type: ignore
to_fahrenheit.celsius_format = "%.f°C"  # type: ignore

to_fahrenheit.flag__edit_type = "toggle"  # type: ignore

# And we run the function with the GUI
fiatlight.fiat_run(to_fahrenheit)
