import fiatlight as fl


def only_lowercase(s: str) -> fl.DataValidationResult:
    if s.isupper():
        return fl.DataValidationResult.ok()
    return fl.DataValidationResult.error("The string should be lowercase.")


def main() -> None:
    @fl.with_custom_attrs(s__validate_value=only_lowercase)
    def f(s: str = "") -> str:
        return s

    fl.fiat_run(f)


if __name__ == "__main__":
    main()
