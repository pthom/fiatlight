import fiatlight as fl


def only_lowercase(s: str) -> fl.DataValidationResult:
    if s.islower():
        return fl.DataValidationResult.ok()
    return fl.DataValidationResult.error("The string should be lowercase.")


def main() -> None:
    @fl.with_fiat_attributes(s__validate_value=only_lowercase)
    def f(s: str = "") -> str:
        return s

    fl.run(f)


if __name__ == "__main__":
    main()
