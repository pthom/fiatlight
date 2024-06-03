import logging

import fiatlight
from fiatlight import FunctionWithGui


def usability_unexpected_none_output() -> None:
    """`f` signature lies! It may unexpectedly return None.

    fiatlight should catch this, and:
        - display an error which can be debugged by the user
        - not call the next function (g) if the previous one (f) returned an unexpected None
    """

    def f(x: int = 1) -> int:
        if x < 0:
            return None  # type: ignore
        return x + 1

    def g(x: int) -> int:
        return x + 3

    fiatlight.run([f, g])


def usability_unexpected_none_input() -> None:
    """In this example, f signatures does not lie (it return an optional),
    but g does not expect to receive an optional.

      fiatlight:
       - call the next function (g)
       - catch and display the exception message
       - propose to debug the error by clicking the button "Debug this exception"
    """

    def f(x: int = 1) -> int | None:
        if x < 0:
            return None
        return x + 1

    def g(x: int) -> int:
        return x + 3

    fiatlight.run([f, g])


def usability_unexpected_none_input_with_change_callback() -> None:
    """In this example, f signatures does not lie (it return an optional),
    but g does not expect to receive an optional.

    g also has a change callback, which should not be called if g receives an unexpected None.
    """

    def f(x: int = 1) -> int | None:
        if x < 0:
            return None
        return x + 1

    def g(x: int) -> int:
        return x + 3

    g_gui = FunctionWithGui(g)

    def on_change(value: int) -> None:
        assert isinstance(value, int)  # This should not be called if g receives an unexpected None
        logging.info(f"Value changed to {value}")

    g_gui.input("x").callbacks.on_change = on_change

    fiatlight.run([f, g_gui])


def usability_expected_none() -> None:
    """`f` signature is honest. It may return None.

    fiatlight should detect that f is returning an optional, and allow this.
    """

    def f(x: int = 1) -> int | None:
        if x < 0:
            return None
        return x + 1

    def g(x: int | None) -> int:
        if x is None:
            return 1000
        return x + 3

    fiatlight.run([f, g])


if __name__ == "__main__":
    # usability_unexpected_none_output()
    # usability_unexpected_none_input()
    usability_unexpected_none_input_with_change_callback()
    # usability_expected_none()
