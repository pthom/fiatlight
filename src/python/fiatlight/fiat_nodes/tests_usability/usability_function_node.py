import fiatlight as fl


def usability_easy() -> None:
    def f(x: int) -> int:
        return x

    fl.run(f)


def usability_with_default_value() -> None:
    def f(x: int = 3) -> int:
        return x

    fl.run(f)


if __name__ == "__main__":
    usability_easy()
    # usability_with_default_value()
