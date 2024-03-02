from fiatlight import FunctionWithGui
from fiatlight.function_node import FunctionNode, FunctionNodeLink
from fiatlight.fiatlight_types import PureFunction, JsonDict
from fiatlight.to_gui import any_function_to_function_with_gui


class FunctionsGraph:
    """A graph of FunctionNodes
    This contains a graph of FunctionNodes modeled as a list of FunctionNode and a list of FunctionNodeLink
    (which are the links between the outputs of a FunctionNode and the inputs of another FunctionNode)

    This class only stores the data representation of the graph, and does not deal with its GUI representation
    (for this, see FunctionGraphGui)

    This class is not meant to be instantiated directly. Use the factory methods instead.
    """

    functions_nodes: list[FunctionNode]
    functions_nodes_links: list[FunctionNodeLink]

    _secret_key: str = "FunctionsGraph"

    def __init__(self, secret_key: str = "FunctionsGraph") -> None:
        if secret_key != self._secret_key:
            raise ValueError("This class should not be instantiated directly. Use the factory method instead.")
        self.functions_nodes = []
        self.functions_nodes_links = []

    def function_unique_name(self, function_node: FunctionNode) -> str:
        """Make sure all names are unique"""
        names = [fn.function_with_gui.name for fn in self.functions_nodes]
        duplicated_names = [name for name in names if names.count(name) > 1]
        if function_node.function_with_gui.name not in duplicated_names:
            return function_node.function_with_gui.name
        else:
            functions_with_same_name = [
                fn for fn in self.functions_nodes if fn.function_with_gui.name == function_node.function_with_gui.name
            ]
            this_function_idx = functions_with_same_name.index(function_node)
            return f"{function_node.function_with_gui.name}_{this_function_idx + 1}"

        # for duplicated_name in duplicated_names:
        #     functions_with_duplicated_name = [fn for fn in self.functions_nodes if fn.unique_name == duplicated_name]
        #     for i, fn in enumerate(functions_with_duplicated_name):
        #         fn.unique_name = f"{fn.unique_name}_{i}"

    def _add_function_with_gui(self, f_gui: FunctionWithGui) -> None:
        # Make sure all names are unique (is this useful?)
        f_node = FunctionNode(f_gui, f_gui.name)
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
        * The output[0] of one should be the input[0] of the next
        """
        r: FunctionsGraph

        # Fill the functions
        def fill_functions_with_gui() -> None:
            for f in functions:
                r._add_function(f)

        def fill_links() -> None:
            r.functions_nodes_links = []
            for i in range(len(r.functions_nodes) - 1):
                fn = r.functions_nodes[i]
                fn_next = r.functions_nodes[i + 1]

                link = FunctionNodeLink(
                    src_function_node=fn,
                    src_output_idx=0,
                    dst_function_node=fn_next,
                    dst_input_name=fn_next.function_with_gui.inputs_with_gui[0].name,
                )
                fn.add_output_link(link)
                fn_next.add_input_link(link)
                r.functions_nodes_links.append(link)

        r = FunctionsGraph(secret_key=FunctionsGraph._secret_key)
        fill_functions_with_gui()
        fill_links()
        return r

    def to_json(self) -> JsonDict:
        """We do not save the links, only the values stored inside the functions."""
        data = {
            "functions_nodes": [fn.function_with_gui.to_json() for fn in self.functions_nodes],
        }
        return data

    def fill_from_json(self, json_data: JsonDict) -> None:
        nodes_data = json_data["functions_nodes"]
        if len(nodes_data) != len(self.functions_nodes):
            raise ValueError("The number of functions in the json does not match the number of functions in the graph")

        for i, fn in enumerate(self.functions_nodes):
            fn.function_with_gui.fill_from_json(nodes_data[i])


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
