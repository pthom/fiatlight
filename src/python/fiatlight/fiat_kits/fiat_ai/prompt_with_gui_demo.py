from fiatlight.fiat_kits.fiat_ai import Prompt


def main() -> None:
    def f(prompt: Prompt) -> str:
        return prompt

    import fiatlight

    fiatlight.run(f, use_node_editor_if_one_function=False)


if __name__ == "__main__":
    main()
