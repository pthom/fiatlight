import fiatlight as fl


def only_lowercase(s: str) -> str:
    if s.isupper():
        raise ValueError("The string should be lowercase.")
    return s


def main() -> None:
    @fl.with_fiat_attributes(s__validator=only_lowercase)
    def f(s: str = "") -> str:
        return s

    fl.run(f)


if __name__ == "__main__":
    main()
