import fiatlight as fl


def only_lowercase(s: str) -> None:
    if s.isupper():
        raise ValueError("The string should be lowercase.")


def main() -> None:
    @fl.with_fiat_attributes(s__validate_value=only_lowercase)
    def f(s: str = "") -> str:
        return s

    fl.run(f)


if __name__ == "__main__":
    main()
