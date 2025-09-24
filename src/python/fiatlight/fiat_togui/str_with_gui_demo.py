import fiatlight as fl


def only_lowercase(s: str) -> str:
    if not s.islower():
        raise ValueError("The string should be lowercase.")
    return s


@fl.with_fiat_attributes(
    #  Validation
    name__validator=only_lowercase,
    #  Fiat attributes
    name__width_em=10.0,
    name__hint="Enter your name",
    name__allow_multiline_edit=False,
    name__resizable=True,
)
def greet(name: str = "") -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"


def main() -> None:
    fl.run(greet)


if __name__ == "__main__":
    main()
