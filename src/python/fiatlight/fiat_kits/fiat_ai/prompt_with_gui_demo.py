from fiatlight.fiat_kits.fiat_ai import Prompt


def main() -> None:
    def f(prompt: Prompt) -> None:
        pass

    import fiatlight

    fiatlight.fiat_run(f)


if __name__ == "__main__":
    main()