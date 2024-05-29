import fiatlight


def test_numeric_ranges_with_manual_custom_attr() -> None:
    def to_fahrenheit(celsius: float = 10) -> float:
        return celsius * 9 / 5 + 32

    to_fahrenheit.celsius__range = (-20, 60)  # type: ignore

    f_gui = fiatlight.FunctionWithGui(to_fahrenheit)

    celsius_gui = f_gui.input("celsius")
    assert celsius_gui.custom_attrs["range"] == (-20, 60)


def test_numeric_ranges_with_decorator_custom_attrs() -> None:
    import fiatlight as fl
    import math

    @fl.with_custom_attrs(x__range=(0.0, 10.0))
    def f(x: float) -> float:
        return math.sin(x)

    f_gui = fl.FunctionWithGui(f)
    x_custom_attrs = f_gui.input("x").custom_attrs
    assert "range" in x_custom_attrs
    assert x_custom_attrs["range"] == (0.0, 10.0)


def test_custom_ranges_optional() -> None:
    def to_fahrenheit(celsius: float | None = 10) -> float:
        if celsius is None:
            return 0
        return celsius * 9 / 5 + 32

    to_fahrenheit.celsius__range = (-20, 60)  # type: ignore

    from fiatlight.fiat_togui.composite_gui import OptionalWithGui

    f_gui = fiatlight.FunctionWithGui(to_fahrenheit)

    celsius_gui = f_gui.input("celsius")
    assert isinstance(celsius_gui, OptionalWithGui)
    assert celsius_gui.inner_gui.custom_attrs["range"] == (-20, 60)
