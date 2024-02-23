from fiatlight import FunctionWithGui
from fiatlight.fiatlight_types import PureFunction
from fiatlight.to_gui import any_function_to_function_with_gui


class FunctionsLink:
    source: FunctionWithGui
    source_output_id: str
    target: FunctionWithGui
    target_input_id: str

    def __init__(
        self, source: FunctionWithGui, source_output_id: str, target: FunctionWithGui, target_input_id: str
    ) -> None:
        self.source = source
        self.source_output_id = source_output_id
        self.target = target
        self.target_input_id = target_input_id

        assert source_output_id in source.all_outputs_ids()
        assert target_input_id in target.all_inputs_ids()


class FunctionsGraph:
    functions: list[FunctionWithGui]
    links: list[FunctionsLink]

    _secret_key: str = "FunctionsGraph"

    def __init__(self, secret_key: str = "FunctionsGraph") -> None:
        if secret_key != self._secret_key:
            raise ValueError("This class should not be instantiated directly. Use the factory method instead.")

    @staticmethod
    def from_function_composition(functions: list[PureFunction]) -> "FunctionsGraph":
        """Create a FunctionsGraph from a list of PureFunctions([InputType] -> OutputType)
        * They should all be pure functions
        * They should all accept a single input (InputType), except the first one, which can accept multiple inputs
        * They should all return a single value (OutputType)
        * They should all be composable: the output type of one should be the input type of the next
        """
        r: FunctionsGraph

        # Fill the functions
        def fill_functions_with_gui() -> None:
            r.functions = [any_function_to_function_with_gui(f) for f in functions]

        def check_functions_input_output() -> None:
            # They should all accept a single input (InputType), except the first one, which can accept multiple inputs
            for i, f in enumerate(r.functions):
                if i != 0:
                    assert len(f.inputs_with_gui) == 1

            # They should all return a single value (OutputType)
            for f in r.functions:
                assert len(f.outputs_with_gui) == 1

            # They should all be composable: the output type of one should be the input type of the next
            # Not implemented yet, since we don't have the type information yet
            # fn_pairs = functional_utils.overlapping_pairs(r.functions)
            # for fn0, fn1 in fn_pairs:
            #     assert fn0.outputs_with_gui[0].parameter_with_gui.typeclass == fn1.inputs_with_gui[0].parameter_with_gui.typeclass

        def fill_links() -> None:
            r.links = []
            for i in range(len(r.functions) - 1):
                fn = r.functions[i]
                fn_next = r.functions[i + 1]

                link = FunctionsLink(
                    source=fn,
                    source_output_id=fn.outputs_with_gui[0].name,
                    target=fn_next,
                    target_input_id=fn_next.inputs_with_gui[0].name,
                )
                r.links.append(link)

        r = FunctionsGraph(secret_key=FunctionsGraph._secret_key)
        fill_functions_with_gui()
        check_functions_input_output()
        fill_links()
        return r


def sandbox() -> None:
    def add(a: int, b: int = 2) -> int:
        return a + b

    def mul2(a: int) -> int:
        return a * 2

    def div3(a: int) -> float:
        return a / 3

    fg = FunctionsGraph.from_function_composition([add, mul2, div3])
    print(fg.functions)
    print(fg.links)


if __name__ == "__main__":
    sandbox()
