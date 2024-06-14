import fiatlight as fl


def only_lowercase(s: str) -> fl.DataValidationResult:
    if s.islower():
        return fl.DataValidationResult.ok()
    return fl.DataValidationResult.error("The string should be lowercase.")


@fl.with_fiat_attributes(
    #  Validation
    name__validate_value=only_lowercase,
    #  Custom attributes
    name__width_em=10.0,
    name__hint="Enter your name",
    name__allow_multiline_edit=False,
    name__resizable=True,
)
def greet(name: str = "") -> str:
    return f"Hello, {name}!"


def main() -> None:
    fl.run(greet)


if __name__ == "__main__":
    main()
