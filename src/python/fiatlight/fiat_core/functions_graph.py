from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.function_node import FunctionNode, FunctionNodeLink
from fiatlight.fiat_types import Function, JsonDict, GlobalsDict, LocalsDict
from fiatlight.fiat_core.to_gui import to_function_with_gui

from typing import Sequence, Dict


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

    @staticmethod
    def create_empty() -> "FunctionsGraph":
        return FunctionsGraph(secret_key=FunctionsGraph._secret_key)

    @staticmethod
    def from_function_composition(
        functions: Sequence[Function | FunctionWithGui],
        globals_dict: GlobalsDict | None = None,
        locals_dict: LocalsDict | None = None,
    ) -> "FunctionsGraph":
        """Create a FunctionsGraph from a list of PureFunctions([InputType] -> OutputType)
        * They should all be pure functions
        * The output[0] of one should be the input[0] of the next
        """
        return FunctionsGraph._create_from_function_composition(
            functions, globals_dict=globals_dict, locals_dict=locals_dict
        )

    def add_function_composition(
        self,
        functions: Sequence[Function | FunctionWithGui],
        globals_dict: GlobalsDict | None = None,
        locals_dict: LocalsDict | None = None,
    ) -> None:
        composition = FunctionsGraph.from_function_composition(
            functions, globals_dict=globals_dict, locals_dict=locals_dict
        )
        self.merge_graph(composition)

    def add_function(
        self,
        f: Function | FunctionWithGui,
        globals_dict: GlobalsDict | None = None,
        locals_dict: LocalsDict | None = None,
    ) -> None:
        if isinstance(f, FunctionWithGui):
            self._add_function_with_gui(f)
        else:
            self._add_function(f, globals_dict=globals_dict, locals_dict=locals_dict)

    def add_link(
        self, src_function_name: str, dst_function_name: str, dst_input_name: str | None = None, src_output_idx: int = 0
    ) -> None:
        """Add a link between two functions"""
        src_function = self.function_node_with_unique_name(src_function_name)
        dst_function = self.function_node_with_unique_name(dst_function_name)

        if src_output_idx >= len(src_function.function_with_gui.outputs_with_gui):
            raise ValueError(
                f"Output index {src_output_idx} is out of range for function {src_function_name}. "
                f"Function {src_function_name} has {len(src_function.function_with_gui.outputs_with_gui)} outputs."
            )
        if dst_input_name is not None:
            if not any(
                dst_input_name == input_with_gui.name
                for input_with_gui in dst_function.function_with_gui.inputs_with_gui
            ):
                raise ValueError(
                    f"Input {dst_input_name} not found in function {dst_function_name}. "
                    f"Available inputs: {[input_with_gui.name for input_with_gui in dst_function.function_with_gui.inputs_with_gui]}"
                )
        if dst_input_name is None:
            if len(dst_function.function_with_gui.inputs_with_gui) == 0:
                raise ValueError(
                    f"Function {dst_function_name} has no inputs. " f"Please specify the input name to link to."
                )
            dst_input_name = dst_function.function_with_gui.inputs_with_gui[0].name

        link = FunctionNodeLink(
            src_function_node=src_function,
            src_output_idx=src_output_idx,
            dst_function_node=dst_function,
            dst_input_name=dst_input_name,
        )
        src_function.add_output_link(link)
        dst_function.add_input_link(link)
        self.functions_nodes_links.append(link)

    def function_node_unique_name(self, function_node: FunctionNode) -> str:
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

    def function_node_with_unique_name(self, function_name: str) -> FunctionNode:
        """Get the function with the unique name"""
        for fn in self.functions_nodes:
            if self.function_node_unique_name(fn) == function_name:
                return fn
        raise ValueError(f"No function with the name {function_name}")

    def all_function_nodes_with_unique_names(self) -> Dict[str, FunctionNode]:
        return {self.function_node_unique_name(fn): fn for fn in self.functions_nodes}

    def _add_function_with_gui(self, f_gui: FunctionWithGui) -> None:
        # Make sure all names are unique (is this useful?)
        f_node = FunctionNode(f_gui, f_gui.name)
        self.functions_nodes.append(f_node)

    def _add_function(
        self,
        f: Function,
        globals_dict: GlobalsDict | None = None,
        locals_dict: LocalsDict | None = None,
    ) -> None:
        f_gui = to_function_with_gui(f, globals_dict=globals_dict, locals_dict=locals_dict)
        self._add_function_with_gui(f_gui)

    def merge_graph(self, other: "FunctionsGraph") -> None:
        self.functions_nodes.extend(other.functions_nodes)
        self.functions_nodes_links.extend(other.functions_nodes_links)

    @staticmethod
    def _create_from_function_composition(
        functions: Sequence[Function | FunctionWithGui],
        globals_dict: GlobalsDict | None = None,
        locals_dict: LocalsDict | None = None,
    ) -> "FunctionsGraph":
        """Create a FunctionsGraph from a list of PureFunctions([InputType] -> OutputType)
        * They should all be pure functions
        * The output[0] of one should be the input[0] of the next
        """

        # Make sure we don't modify the user namespace
        if globals_dict is not None:
            globals_dict = globals_dict.copy()
        if locals_dict is not None:
            locals_dict = locals_dict.copy()

        r: FunctionsGraph

        # Fill the functions
        def fill_functions_with_gui() -> None:
            for f in functions:
                if isinstance(f, FunctionWithGui):
                    r._add_function_with_gui(f)
                else:
                    r._add_function(f, globals_dict=globals_dict, locals_dict=locals_dict)

        def fill_links() -> None:
            r.functions_nodes_links = []
            for i in range(len(r.functions_nodes) - 1):
                fn = r.functions_nodes[i]
                fn_next = r.functions_nodes[i + 1]
                if (
                    len(fn.function_with_gui.outputs_with_gui) >= 1
                    and len(fn_next.function_with_gui.inputs_with_gui) >= 1
                ):
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

    def save_user_inputs_to_json(self) -> JsonDict:
        """Saves the user inputs, i.e. the functions params that are editable in the GUI
        (this excludes the params that are set by the links between the functions)"""
        fn_data = {}
        for function_node in self.functions_nodes:
            fn_data[self.function_node_unique_name(function_node)] = function_node.save_user_inputs_to_json()
        return {"functions_nodes": fn_data}

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        """Restores the user inputs from a json dict"""
        if "functions_nodes" not in json_data:
            return
        fn_data = json_data["functions_nodes"]
        for unique_name, fn_json in fn_data.items():
            fn = self.function_node_with_unique_name(unique_name)
            fn.load_user_inputs_from_json(fn_json)

    def invoke_top_leaf_functions(self) -> None:
        """Invoke all the leaves of the graph"""
        for fn in self.functions_nodes:
            if len(fn.input_links) == 0:
                fn.function_with_gui.dirty = True
                fn.invoke_function()


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