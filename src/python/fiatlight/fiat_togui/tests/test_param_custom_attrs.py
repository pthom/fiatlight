import fiatlight


def test_numeric_ranges() -> None:
    def to_fahrenheit(celsius: float = 10) -> float:
        return celsius * 9 / 5 + 32

    to_fahrenheit.celsius__range = (-20, 60)  # type: ignore
    to_fahrenheit.celsius__edit_type = "knob"  # type: ignore
    to_fahrenheit.celsius_format = "%.f°C"  # type: ignore

    f_gui = fiatlight.FunctionWithGui(to_fahrenheit)

    celsius_gui = f_gui.input("celsius")
    assert celsius_gui.custom_attrs["range"] == (-20, 60)

    # fiatlight.fiat_run(to_fahrenheit)


def test_custom_ranges_optional() -> None:
    def to_fahrenheit(celsius: float | None = 10) -> float:
        if celsius is None:
            return 0
        return celsius * 9 / 5 + 32

    to_fahrenheit.celsius__range = (-20, 60)  # type: ignore

    f_gui = fiatlight.FunctionWithGui(to_fahrenheit)

    celsius_gui = f_gui.input("celsius")
    assert celsius_gui.custom_attrs["range"] == (-20, 60)
