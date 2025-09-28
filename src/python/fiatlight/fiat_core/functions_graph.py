"""FunctionsGraph: A graph of FunctionNodes"""

import copy

from fiatlight.fiat_core.function_with_gui import FunctionWithGui, FunctionWithGuiFactoryFromName
from fiatlight.fiat_core.function_node import FunctionNode, FunctionNodeLink
from fiatlight.fiat_core.gui_node import GuiNode
from fiatlight.fiat_core.markdown_node import MarkdownNode
from fiatlight.fiat_types import Function, JsonDict, GuiFunctionWithInputs

from typing import Sequence, Tuple, Set, List
from pydantic import BaseModel


class FunctionsGraph:
    """A graph of FunctionNodes

     `FunctionsGraph` is one of the core classes of FiatLight: it represents a graph of functions,
     where the output of one function can be linked to the input of another function.

     See its [full code](../fiat_core/functions_graph.py).

    It contains a graph of FunctionNodes modeled as a list of FunctionNode and a list of FunctionNodeLink
    (which are the links between the outputs of a FunctionNode and the inputs of another FunctionNode)

    This class only stores the data representation of the graph, and does not deal with its GUI representation
    (for this, see FunctionGraphGui)

    This class is not meant to be instantiated directly. Use the factory methods instead.

    Public Members
    ==============
    # the list of FunctionNode in the graph
    functions_nodes: list[FunctionNode]
    # the list of links between the FunctionNode
    functions_nodes_links: list[FunctionNodeLink]

    """

    # the list of FunctionNode in the graph
    functions_nodes: list[FunctionNode]
    # the list of links between the FunctionNode
    functions_nodes_links: list[FunctionNodeLink]

    _secret_key: str = "FunctionsGraph"

    class _Construction_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ================================================================================================================
        #                                            Construction (Empty)
        # ================================================================================================================
        """

        pass

    def __init__(self, secret_key: str = "FunctionsGraph") -> None:
        """This class should not be instantiated directly. Use the factory methods instead."""
        if secret_key != self._secret_key:
            raise ValueError(
                "This class should not be instantiated directly. Use the factory methods (from_...) instead."
            )
        self.functions_nodes = []
        self.functions_nodes_links = []

    @staticmethod
    def create_empty() -> "FunctionsGraph":
        """Create an empty FunctionsGraph"""
        return FunctionsGraph(secret_key=FunctionsGraph._secret_key)

    class _Public_API_Add_Function_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ================================================================================================================
        #                                            Public API / Add functions
        #
        # ---------------------------------------------------------------------------------------------------------------
        # Notes:
        #   You can add either Functions or FunctionWithGui
        #     - If f is a FunctionWithGui, it will be added as is
        #     - If f is a standard function:
        #         - it will be wrapped in a FunctionWithGui
        #         - the function signature *must* mention the types of the parameters and the return type
        # ================================================================================================================
        """

        pass

    #
    # IMPORTANT: All user facing that add functions (not FunctionWithGui) should capture the locals and globals
    # of the caller, before passing them to the private _add_function method.
    # This should be done right after being called!
    #

    @staticmethod
    def from_function(f: Function | FunctionWithGui) -> "FunctionsGraph":
        """Create a FunctionsGraph from a single function, either a standard function or a FunctionWithGui"""
        r = FunctionsGraph.create_empty()
        if isinstance(f, FunctionWithGui):
            r._add_function_with_gui(f)
        else:
            r._add_function(f)
        return r

    @staticmethod
    def from_function_composition(functions: Sequence[Function | FunctionWithGui]) -> "FunctionsGraph":
        """Create a FunctionsGraph from a list of functions that will be chained together
        i.e. the output[0] of one function will be the input[0] of the next function
        """
        return FunctionsGraph._create_from_function_composition(functions)

    def add_function_composition(self, functions: Sequence[Function | FunctionWithGui]) -> None:
        """Add a list of functions that will be chained together"""
        composition = FunctionsGraph._create_from_function_composition(functions)
        self.merge_graph(composition)

    def add_function(self, f: Function | FunctionWithGui, label: str | None = None) -> FunctionNode:
        """Add a function to the graph. It will not be linked to any other function. Returns the FunctionNode added."""
        if isinstance(f, FunctionWithGui):
            if label is not None:
                f.label = label
            return self._add_function_with_gui(f)
        else:
            return self._add_function(f, label=label)

    def add_gui_node(
        self,
        gui_function: GuiFunctionWithInputs,
        label: str | None = None,
        gui_serializable_data: BaseModel | None = None,
    ) -> FunctionNode:
        gui_node = GuiNode(gui_function, label=label, gui_serializable_data=gui_serializable_data)
        return self._add_function_with_gui(gui_node)

    def add_markdown_node(
        self,
        md_string: str,
        label: str = "Documentation",
        text_width_em: float = 20.0,
        unindented: bool = True,
    ) -> FunctionNode:
        markdown_node = MarkdownNode(md_string, label=label, text_width_em=text_width_em, unindented=unindented)
        return self._add_function_with_gui(markdown_node)

    class _Private_API_Add_Function_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ================================================================================================================
        #                                            Private API / Add functions
        # ================================================================================================================
        """

        pass

    def _add_function_with_gui(self, f_gui: FunctionWithGui) -> FunctionNode:
        def has_already_function_with_same_name() -> bool:
            for fn in self.functions_nodes:
                if fn.function_with_gui.function_name == f_gui.function_name:
                    return True
            return False

        def f_gui_with_distinct_name() -> FunctionWithGui:
            f_gui_2 = copy.copy(f_gui)
            f_gui_2.function_name = f"{f_gui.function_name}_2"
            return f_gui_2

        if has_already_function_with_same_name():
            r = self._add_function_with_gui(f_gui_with_distinct_name())
            return r

        f_node = FunctionNode(f_gui)
        self.functions_nodes.append(f_node)
        return f_node

    def _add_function(
        self,
        f: Function,
        label: str | None = None,
    ) -> FunctionNode:
        f_gui = FunctionWithGui(f)
        if label is not None:
            f_gui.label = label
        return self._add_function_with_gui(f_gui)

    @staticmethod
    def _create_from_function_composition(functions: Sequence[Function | FunctionWithGui]) -> "FunctionsGraph":
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
                    r._add_function(f)

        def _fill_links() -> None:
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
        _fill_links()
        return r

    class _Graph_Manipulation_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ================================================================================================================
        #                                            Graph manipulation
        # ================================================================================================================
        """

        pass

    def _can_add_link(
        self, src_function_node: FunctionNode, dst_function_node: FunctionNode, dst_input_name: str, src_output_idx: int
    ) -> Tuple[bool, str]:
        """Check if a link can be added between two functions. (private)"""
        # 1. Check that the function nodes are in the graph
        if src_function_node not in self.functions_nodes:
            return False, f"Function {src_function_node.function_with_gui.function_name} not found in the graph"
        if dst_function_node not in self.functions_nodes:
            return False, f"Function {dst_function_node.function_with_gui.function_name} not found in the graph"

        # 2. Check that the output index and input name are valid
        if src_output_idx >= src_function_node.function_with_gui.nb_outputs():
            return (
                False,
                f"Output index {src_output_idx} is out of range for function {src_function_node.function_with_gui.function_name}",
            )
        if dst_input_name not in dst_function_node.function_with_gui.all_inputs_names():
            return (
                False,
                f"Input {dst_input_name} not found in function {dst_function_node.function_with_gui.function_name}",
            )

        # 3. Check that src_function_node and dst_function_node are not the same
        if src_function_node == dst_function_node:
            return False, "Cannot link a function to itself"

        new_link = FunctionNodeLink(
            src_function_node=src_function_node,
            src_output_idx=src_output_idx,
            dst_function_node=dst_function_node,
            dst_input_name=dst_input_name,
        )

        # 4. Check that the link does not already exist
        for link in self.functions_nodes_links:
            if new_link.is_equal(link):
                return False, "Link already exists"

        # 5. Check that this input is not already linked
        if dst_function_node.has_input_link(dst_input_name):
            return (
                False,
                f"Input {dst_input_name} of function {dst_function_node.function_with_gui.function_name} is already linked",
            )

        # 6. Check that the link does not create a cycle
        if self._would_add_cycle(new_link):
            return False, "Link would create a cycle"

        return True, ""

    def _add_link_from_function_nodes(
        self,
        src_function_node: FunctionNode,
        dst_function_node: FunctionNode,
        dst_input_name: str | None = None,
        src_output_idx: int = 0,
    ) -> FunctionNodeLink:
        """Add a link between two functions nodes (private)"""
        src_function_name = src_function_node.function_with_gui.function_name
        dst_function_name = dst_function_node.function_with_gui.function_name

        if src_output_idx >= src_function_node.function_with_gui.nb_outputs():
            raise ValueError(
                f"Output index {src_output_idx} is out of range for function {src_function_name}. "
                f"Function {src_function_name} has {src_function_node.function_with_gui.nb_outputs()} outputs."
            )
        if dst_input_name is not None:
            if dst_input_name not in dst_function_node.function_with_gui.all_inputs_names():
                raise ValueError(
                    f"Input {dst_input_name} not found in function {dst_function_name}. "
                    f"Available inputs: {[dst_function_node.function_with_gui.all_inputs_names()]}"
                )
        if dst_input_name is None:
            if dst_function_node.function_with_gui.nb_inputs() == 0:
                raise ValueError(f"Function {dst_function_name} has no inputs!")
            dst_input_name = dst_function_node.function_with_gui.input_of_idx(0).name

        can_add, fail_reason = self._can_add_link(
            src_function_node, dst_function_node, dst_input_name=dst_input_name, src_output_idx=src_output_idx
        )
        if not can_add:
            raise ValueError(f"Cannot add link from {src_function_name} to {dst_function_name}: {fail_reason}")

        link = FunctionNodeLink(
            src_function_node=src_function_node,
            src_output_idx=src_output_idx,
            dst_function_node=dst_function_node,
            dst_input_name=dst_input_name,
        )
        src_function_node.add_output_link(link)
        dst_function_node.add_input_link(link)
        self.functions_nodes_links.append(link)

        # invoke the src function so that the dst function is updated
        src_function_node.function_with_gui._dirty = True
        src_function_node.call_invoke_async_or_not()

        return link

    def add_link(
        self,
        src_function: str | Function | FunctionWithGui,
        dst_function: str | Function | FunctionWithGui,
        dst_input_name: str | None = None,
        src_output_idx: int = 0,
    ) -> None:
        """Add a link between two functions, which are identified by their *unique* names"""
        src_function_node = self._function_node_with_name_or_is_function(src_function)
        dst_function_node = self._function_node_with_name_or_is_function(dst_function)
        self._add_link_from_function_nodes(
            src_function_node, dst_function_node, dst_input_name=dst_input_name, src_output_idx=src_output_idx
        )

    def merge_graph(self, other: "FunctionsGraph") -> None:
        """Merge another FunctionsGraph into this one"""
        self.functions_nodes.extend(other.functions_nodes)
        self.functions_nodes_links.extend(other.functions_nodes_links)

    def function_with_gui_of_name(self, name: str | None = None) -> FunctionWithGui:
        """Get the function with the given unique name"""
        if name is None:
            assert len(self.functions_nodes) == 1
            return self.functions_nodes[0].function_with_gui
        for fn in self.functions_nodes:
            if fn.function_with_gui.function_name == name:
                return fn.function_with_gui
        raise ValueError(f"No function with the name {name}")

    def _would_add_cycle(self, new_link: FunctionNodeLink) -> bool:
        """Check if adding a link would create a cycle (private)"""
        new_graph = FunctionsGraph.create_empty()
        new_graph.functions_nodes = copy.copy(self.functions_nodes)
        new_graph.functions_nodes_links = copy.copy(self.functions_nodes_links)
        new_graph.functions_nodes_links.append(new_link)

        return new_graph.has_cycle()

    def has_cycle(self) -> bool:
        """Returns True if the graph has a cycle"""
        for fn in self.functions_nodes:
            if self._has_cycle_from_node(fn):
                return True
        return False

    def _has_cycle_from_node(self, fn: FunctionNode, path: Set[FunctionNode] | None = None) -> bool:
        """Check if there is a cycle starting from a given node (private)"""
        if path is None:
            path = set()
        path.add(fn)
        for link in self.functions_nodes_links:
            if link.src_function_node != fn:
                continue
            next_fn = link.dst_function_node
            if next_fn in path:
                return True  # A cycle is found if next_fn is already in the path
            path_copy = copy.copy(path)
            if self._has_cycle_from_node(next_fn, path_copy):
                return True
        path.remove(fn)  # Remove fn from path as we backtrack
        return False

    def _remove_link(self, link: FunctionNodeLink) -> None:
        """Remove a link between two functions (private)"""
        self.functions_nodes_links.remove(link)
        link.src_function_node.output_links.remove(link)
        link.dst_function_node.input_links.remove(link)

    def _remove_function_node(self, function_node: FunctionNode) -> None:
        """Remove a function node from the graph (private)"""
        for link in function_node.output_links:
            self._remove_link(link)
            # for fn_node in self.functions_nodes:
            #     for link2 in fn_node.input_links:
            #         if link2 == link:
            #             fn_node.input_links.remove(link2)
            #     for link3 in fn_node.output_links:
            #         if link3 == link:
            #             fn_node.output_links.remove(link3)
        for link in function_node.input_links:
            self._remove_link(link)
        self.functions_nodes.remove(function_node)

    class _Utilities_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ================================================================================================================
        #                                            Utilities
        # ================================================================================================================
        """

        pass

    def _function_node_with_name_or_is_function(
        self, name_or_function: str | Function | FunctionWithGui
    ) -> FunctionNode:
        """Get the function node with the given name or function"""
        if isinstance(name_or_function, str):
            return self._function_node_with_name(name_or_function)

        elif isinstance(name_or_function, FunctionWithGui):
            fn_with_gui = name_or_function
            candidate_nodes = []
            for fn_node in self.functions_nodes:
                if fn_node.function_with_gui is fn_with_gui:
                    candidate_nodes.append(fn_node)

            if len(candidate_nodes) == 0:
                raise ValueError(f"No function {fn_with_gui}")
            elif len(candidate_nodes) > 1:
                raise ValueError(f"Multiple functions {fn_with_gui}")
            else:
                return candidate_nodes[0]

        else:
            function_reference = name_or_function
            candidate_nodes = []
            for fn_node in self.functions_nodes:
                if fn_node.function_with_gui._f_impl is function_reference:
                    candidate_nodes.append(fn_node)

            if len(candidate_nodes) == 0:
                raise ValueError(f"No function {function_reference}")
            elif len(candidate_nodes) > 1:
                raise ValueError(f"Multiple functions {function_reference}")
            else:
                return candidate_nodes[0]

    def _function_node_with_name(self, function_name: str) -> FunctionNode:
        """Get the function with the unique name"""
        for fn in self.functions_nodes:
            if fn.function_with_gui.function_name == function_name:
                return fn
        raise ValueError(f"No function with the name {function_name}")

    def shall_display_refresh_needed_label(self) -> bool:
        """Returns True if any function node shall display a "Refresh needed" label"""
        r = any(fn.function_with_gui.shall_display_refresh_needed_label() for fn in self.functions_nodes)
        return r

    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ================================================================================================================
        #                                            Serialization
        # Note:  save_gui_options_to_json() and load_gui_options_from_json()
        #        are intentionally not implemented here
        #        See FunctionsGraphGui (which does deals with the GUI)
        # ================================================================================================================
        """

        pass

    def save_user_inputs_to_json(self) -> JsonDict:
        """Saves the user inputs, i.e. the functions params that are editable in the GUI
        (this excludes the params that are set by the links between the functions)"""
        fn_data = {}
        for function_node in self.functions_nodes:
            fn_data[function_node.function_with_gui.function_name] = function_node.save_user_inputs_to_json()
        return {"functions_nodes": fn_data}

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        """Restores the user inputs from a json dict"""
        if "functions_nodes" not in json_data:
            return
        fn_data = json_data["functions_nodes"]
        for function_name, fn_json in fn_data.items():
            fn = self._function_node_with_name(function_name)
            fn.load_user_inputs_from_json(fn_json)

    def save_graph_composition_to_json(self) -> JsonDict:
        """Saves the graph composition to a json dict.
        Only used when the graph composition is editable.
        """

        all_function_names: List[str]
        all_function_names = [fn.function_with_gui.function_name for fn in self.functions_nodes]

        links_data = []
        for link in self.functions_nodes_links:
            src_function_node = link.src_function_node
            dst_function_node = link.dst_function_node
            src_function_name = src_function_node.function_with_gui.function_name
            dst_function_name = dst_function_node.function_with_gui.function_name
            links_data.append(
                {
                    "src_function_name": src_function_name,
                    "dst_function_name": dst_function_name,
                    "dst_input_name": link.dst_input_name,
                    "src_output_idx": link.src_output_idx,
                }
            )
        r = {"functions_names": all_function_names, "functions_nodes_links": links_data}
        return r

    def load_graph_composition_from_json(
        self, json_data: JsonDict, function_factory: FunctionWithGuiFactoryFromName
    ) -> None:
        """Loads the graph composition from a json dict."""
        self.functions_nodes = []
        self.functions_nodes_links = []

        all_function_names = json_data["functions_names"]
        for function_name in all_function_names:
            fn = function_factory(function_name)
            self._add_function_with_gui(fn)

        links_data = json_data["functions_nodes_links"]
        for link_data in links_data:
            src_function_name = link_data["src_function_name"]
            dst_function_name = link_data["dst_function_name"]
            dst_input_name = link_data["dst_input_name"]
            src_output_idx = link_data["src_output_idx"]
            self.add_link(
                src_function_name, dst_function_name, dst_input_name=dst_input_name, src_output_idx=src_output_idx
            )
