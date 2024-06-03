from fiatlight.fiat_kits.fiat_ai import Prompt


def main() -> None:
    def f(prompt: Prompt, s: str) -> str:
        return prompt + s

    import fiatlight

    fiatlight.run(f)


if __name__ == "__main__":
    main()
