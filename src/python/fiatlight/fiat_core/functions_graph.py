from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.function_node import FunctionNode, FunctionNodeLink
from fiatlight.fiat_types import Function, JsonDict, GlobalsDict, LocalsDict
from fiatlight.fiat_core.to_gui import _capture_caller_globals_locals, to_function_with_gui_globals_local_captured

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

    # ================================================================================================================
    #                                            Construction (Empty)
    # ================================================================================================================
    def __init__(self, secret_key: str = "FunctionsGraph") -> None:
        if secret_key != self._secret_key:
            raise ValueError("This class should not be instantiated directly. Use the factory method instead.")
        self.functions_nodes = []
        self.functions_nodes_links = []

    @staticmethod
    def create_empty() -> "FunctionsGraph":
        return FunctionsGraph(secret_key=FunctionsGraph._secret_key)

    # ================================================================================================================
    #                                            Public API / Add functions
    # ================================================================================================================
    #
    # IMPORTANT: All user facing that add functions (not FunctionWithGui) should capture the locals and globals
    # of the caller, before passing them to the private _add_function method.
    # This should be done right after being called!
    @staticmethod
    def from_function(f: Function | FunctionWithGui) -> "FunctionsGraph":
        r = FunctionsGraph.create_empty()
        if isinstance(f, FunctionWithGui):
            r._add_function_with_gui(f)
        else:
            globals_dict, locals_dict = _capture_caller_globals_locals()
            r._add_function(f, globals_dict=globals_dict, locals_dict=locals_dict)
        return r

    @staticmethod
    def from_function_composition(functions: Sequence[Function | FunctionWithGui]) -> "FunctionsGraph":
        """Create a FunctionsGraph from a list of PureFunctions([InputType] -> OutputType)
        * They should all be pure functions
        * The output[0] of one should be the input[0] of the next
        """
        globals_dict, locals_dict = _capture_caller_globals_locals()
        return FunctionsGraph._create_from_function_composition(
            functions, globals_dict=globals_dict, locals_dict=locals_dict
        )

    def add_function_composition(self, functions: Sequence[Function | FunctionWithGui]) -> None:
        globals_dict, locals_dict = _capture_caller_globals_locals()
        composition = FunctionsGraph._create_from_function_composition(
            functions, globals_dict=globals_dict, locals_dict=locals_dict
        )
        self.merge_graph(composition)

    def add_function(self, f: Function | FunctionWithGui) -> None:
        if isinstance(f, FunctionWithGui):
            self._add_function_with_gui(f)
        else:
            globals_dict, locals_dict = _capture_caller_globals_locals()
            self._add_function(f, globals_dict=globals_dict, locals_dict=locals_dict)

    # ================================================================================================================
    #                                            Private API / Add functions
    # ================================================================================================================
    def _add_function_with_gui(self, f_gui: FunctionWithGui) -> None:
        f_node = FunctionNode(f_gui)
        self.functions_nodes.append(f_node)

    def _add_function(
        self,
        f: Function,
        globals_dict: GlobalsDict,
        locals_dict: LocalsDict,
    ) -> None:
        f_gui = to_function_with_gui_globals_local_captured(f, globals_dict=globals_dict, locals_dict=locals_dict)
        self._add_function_with_gui(f_gui)

    @staticmethod
    def _create_from_function_composition(
        functions: Sequence[Function | FunctionWithGui],
        globals_dict: GlobalsDict,
        locals_dict: LocalsDict,
    ) -> "FunctionsGraph":
        """Create a FunctionsGraph from a list of PureFunctions([InputType] -> OutputType)
        * They should all be pure functions
        * The output[0] of one should be the input[0] of the next
        """

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
                if fn.function_with_gui.nb_outputs() >= 1 and fn_next.function_with_gui.nb_inputs() >= 1:
                    link = FunctionNodeLink(
                        src_function_node=fn,
                        src_output_idx=0,
                        dst_function_node=fn_next,
                        dst_input_name=fn_next.function_with_gui.input_of_idx(0).name,
                    )
                    fn.add_output_link(link)
                    fn_next.add_input_link(link)
                    r.functions_nodes_links.append(link)

        r = FunctionsGraph(secret_key=FunctionsGraph._secret_key)
        fill_functions_with_gui()
        fill_links()
        return r

    # ================================================================================================================
    #                                            Graph manipulation
    # ================================================================================================================
    def add_link(
        self, src_function_name: str, dst_function_name: str, dst_input_name: str | None = None, src_output_idx: int = 0
    ) -> None:
        """Add a link between two functions"""
        src_function = self._function_node_with_unique_name(src_function_name)
        dst_function = self._function_node_with_unique_name(dst_function_name)

        if src_output_idx >= src_function.function_with_gui.nb_outputs():
            raise ValueError(
                f"Output index {src_output_idx} is out of range for function {src_function_name}. "
                f"Function {src_function_name} has {src_function.function_with_gui.nb_outputs()} outputs."
            )
        if dst_input_name is not None:
            if dst_input_name not in dst_function.function_with_gui.all_inputs_names():
                raise ValueError(
                    f"Input {dst_input_name} not found in function {dst_function_name}. "
                    f"Available inputs: {[dst_function.function_with_gui.all_inputs_names()]}"
                )
        if dst_input_name is None:
            if dst_function.function_with_gui.nb_inputs() == 0:
                raise ValueError(f"Function {dst_function_name} has no inputs!")
            dst_input_name = dst_function.function_with_gui.input_of_idx(0).name

        link = FunctionNodeLink(
            src_function_node=src_function,
            src_output_idx=src_output_idx,
            dst_function_node=dst_function,
            dst_input_name=dst_input_name,
        )
        src_function.add_output_link(link)
        dst_function.add_input_link(link)
        self.functions_nodes_links.append(link)

    def merge_graph(self, other: "FunctionsGraph") -> None:
        self.functions_nodes.extend(other.functions_nodes)
        self.functions_nodes_links.extend(other.functions_nodes_links)

    def function_with_gui(self, name: str | None = None) -> FunctionWithGui:
        if name is None:
            assert len(self.functions_nodes) == 1
            return self.functions_nodes[0].function_with_gui
        for fn in self.functions_nodes:
            if fn.function_with_gui.name == name:
                return fn.function_with_gui
        raise ValueError(f"No function with the name {name}")

    # ================================================================================================================
    #                                            Node unique names
    # ================================================================================================================
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

    def _function_node_with_unique_name(self, function_name: str) -> FunctionNode:
        """Get the function with the unique name"""
        for fn in self.functions_nodes:
            if self.function_node_unique_name(fn) == function_name:
                return fn
        raise ValueError(f"No function with the name {function_name}")

    def _all_function_nodes_with_unique_names(self) -> Dict[str, FunctionNode]:
        return {self.function_node_unique_name(fn): fn for fn in self.functions_nodes}

    # ================================================================================================================
    #                                            Invoke all functions
    # ================================================================================================================
    def invoke_all_functions(self) -> None:
        """Invoke all the functions of the graph"""

        # We need to do this in two steps:
        # 1. Mark all functions as dirty (so that the call to invoke_function will actually call the function)
        for fn in self.functions_nodes:
            fn.function_with_gui._dirty = True

        # 2. Invoke all the functions
        # This is done in a separate loop because the functions may depend on each other,
        # and a call to fn.invoke_function() may trigger a call to other functions
        # (and mark them as not dirty anymore as a side effect)
        for fn in self.functions_nodes:
            if fn.function_with_gui.is_dirty():
                fn.invoke_function()

    # ================================================================================================================
    #                                            Save user inputs
    # ================================================================================================================
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
            fn = self._function_node_with_unique_name(unique_name)
            fn.load_user_inputs_from_json(fn_json)


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
