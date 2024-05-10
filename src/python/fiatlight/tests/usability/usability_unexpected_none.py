import fiatlight


def sandbox_unexpected_none() -> None:
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

    fiatlight.fiat_run_composition([f, g])


def sandbox_expected_none():
    """`f` signature is honest. It may return None.

    fiatlight should detect that f is returning an optional, and allow this.
    """

    def f(x: int = 1) -> int | None:
        if x < 0:
            return None  # type: ignore
        return x + 1

    def g(x: int | None) -> int:
        if x is None:
            return 1000
        return x + 3

    fiatlight.fiat_run_composition([f, g])


if __name__ == "__main__":
    # sandbox_unexpected_none()
    sandbox_expected_none()
