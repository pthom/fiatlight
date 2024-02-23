from fiatlight import FunctionWithGui
from fiatlight.function_node import FunctionNode, FunctionNodeLink
from fiatlight.fiatlight_types import PureFunction
from fiatlight.to_gui import any_function_to_function_with_gui


class FunctionsGraph:
    functions_nodes: list[FunctionNode]
    functions_nodes_links: list[FunctionNodeLink]

    _secret_key: str = "FunctionsGraph"

    def __init__(self, secret_key: str = "FunctionsGraph") -> None:
        if secret_key != self._secret_key:
            raise ValueError("This class should not be instantiated directly. Use the factory method instead.")
        self.functions_nodes = []
        self.functions_nodes_links = []

    def _add_function_with_gui(self, f_gui: FunctionWithGui) -> None:
        # Make sure all names are unique (is this useful?)
        all_names = [f.name for f in self.functions_nodes]
        unique_name = f_gui.name if f_gui.name not in all_names else f_gui.name + "-" + str(len(all_names))

        f_node = FunctionNode(f_gui, unique_name)
        self.functions_nodes.append(f_node)

    def _add_function(self, f: PureFunction) -> None:
        f_gui = any_function_to_function_with_gui(f)
        self._add_function_with_gui(f_gui)

    def add_function_composition(self, functions: list[PureFunction]) -> None:
        composition = FunctionsGraph.from_function_composition(functions)
        self.merge_graph(composition)

    def merge_graph(self, other: "FunctionsGraph") -> None:
        self.functions_nodes.extend(other.functions_nodes)
        self.functions_nodes_links.extend(other.functions_nodes_links)

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
            for f in functions:
                r._add_function(f)

        def check_functions_input_output() -> None:
            # They should all accept a single input (InputType), except the first one, which can accept multiple inputs
            for i, f in enumerate(r.functions_nodes):
                if i != 0:
                    assert len(f.function_with_gui.inputs_with_gui) == 1

            # They should all return a single value (OutputType)
            for f in r.functions_nodes:
                assert len(f.function_with_gui.outputs_with_gui) == 1

            # They should all be composable: the output type of one should be the input type of the next
            # Not implemented yet, since we don't have the type information yet
            # fn_pairs = functional_utils.overlapping_pairs(r.functions)
            # for fn0, fn1 in fn_pairs:
            #     assert fn0.outputs_with_gui[0].parameter_with_gui.typeclass == fn1.inputs_with_gui[0].parameter_with_gui.typeclass

        def fill_links() -> None:
            r.functions_nodes_links = []
            for i in range(len(r.functions_nodes) - 1):
                fn = r.functions_nodes[i]
                fn_next = r.functions_nodes[i + 1]

                link = FunctionNodeLink(
                    src_function_node=fn,
                    src_output_name=fn.function_with_gui.outputs_with_gui[0].name,
                    dst_function_node=fn_next,
                    dst_input_name=fn_next.function_with_gui.inputs_with_gui[0].name,
                )
                fn.add_output_link(link)
                fn_next.add_input_link(link)
                r.functions_nodes_links.append(link)

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

    fg = FunctionsGraph.from_function_composition([add, mul2, mul2, div3])
    print(fg.functions_nodes)
    print(fg.functions_nodes_links)


if __name__ == "__main__":
    sandbox()
