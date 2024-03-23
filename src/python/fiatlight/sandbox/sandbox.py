import fiatlight


def f(prompt: str) -> int:
    return len(prompt)


def main() -> None:
    f_gui = fiatlight.any_function_to_function_with_gui(f)
    prompt_input = f_gui.input_of_name("prompt")
    assert isinstance(prompt_input, fiatlight.core.StrWithGui)
    prompt_input.params.edit_type = fiatlight.core.StrEditType.multiline
    prompt_input.params.width_em = 60

    graph = fiatlight.FunctionsGraph.from_function_composition([f_gui])
    fiatlight.fiat_run(graph)


if __name__ == "__main__":
    main()
