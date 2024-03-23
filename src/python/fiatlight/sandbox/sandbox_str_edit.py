from fiatlight import fiat_core
import fiatlight


def f(prompt: str) -> int:
    return len(prompt)


def main() -> None:
    f_gui = fiatlight.to_function_with_gui(f)
    prompt_input = f_gui.input_of_name("prompt")
    assert isinstance(prompt_input, fiat_core.StrWithGui)
    prompt_input.params.edit_type = fiat_core.StrEditType.multiline
    # prompt_input.params.width_em = 60

    graph = fiatlight.FunctionsGraph.from_function_composition([f_gui])
    fiatlight.fiat_run(graph)


if __name__ == "__main__":
    main()
