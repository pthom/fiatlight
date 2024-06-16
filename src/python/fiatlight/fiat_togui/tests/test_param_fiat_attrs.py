import fiatlight


def test_numeric_ranges_with_manual_fiat_attr() -> None:
    def to_fahrenheit(celsius: float = 10) -> float:
        return celsius * 9 / 5 + 32

    to_fahrenheit.celsius__range = (-20, 60)  # type: ignore

    f_gui = fiatlight.FunctionWithGui(to_fahrenheit)

    celsius_gui = f_gui.input("celsius")
    assert celsius_gui.fiat_attributes["range"] == (-20, 60)


def test_numeric_ranges_with_decorator_fiat_attrs() -> None:
    import fiatlight as fl
    import math

    @fl.with_fiat_attributes(x__range=(0.0, 10.0))
    def f(x: float) -> float:
        return math.sin(x)

    f_gui = fl.FunctionWithGui(f)
    x_fiat_attrs = f_gui.input("x").fiat_attributes
    assert "range" in x_fiat_attrs
    assert x_fiat_attrs["range"] == (0.0, 10.0)


def test_custom_ranges_optional() -> None:
    def to_fahrenheit(celsius: float | None = 10) -> float:
        if celsius is None:
            return 0
        return celsius * 9 / 5 + 32

    to_fahrenheit.celsius__range = (-20, 60)  # type: ignore

    from fiatlight.fiat_togui.optional_with_gui import OptionalWithGui

    f_gui = fiatlight.FunctionWithGui(to_fahrenheit)

    celsius_gui = f_gui.input("celsius")
    assert isinstance(celsius_gui, OptionalWithGui)
    assert celsius_gui.inner_gui.fiat_attributes["range"] == (-20, 60)
