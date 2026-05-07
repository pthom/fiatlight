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

    # Monotonic counter for minting stable node ids (`n1`, `n2`, …). Never reused,
    # even after a node is removed, so saved data keyed by old ids cannot accidentally
    # bind to a different node later.
    _stable_id_counter: int = 0

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
        self._stable_id_counter = 0

    def _next_stable_id(self) -> str:
        """Mint a fresh stable id (`n1`, `n2`, …). Never reused, even after a node is removed."""
        self._stable_id_counter += 1
        return f"n{self._stable_id_counter}"

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

    def _add_function_with_gui(self, f_gui: FunctionWithGui, stable_id: str | None = None) -> FunctionNode:
        # Two nodes wrapping the same function are allowed and share their
        # display name. They are distinguished by their stable_id, which is
        # the key used everywhere persistent state lives.
        if stable_id is None:
            stable_id = self._next_stable_id()
        elif stable_id.startswith("n"):
            # Keep the counter ahead of any explicitly-supplied id so a
            # subsequent _next_stable_id() can't collide with what the loader
            # just inserted. Non-`n<int>` ids (custom schemes) leave it alone.
            try:
                n = int(stable_id[1:])
                if n > self._stable_id_counter:
                    self._stable_id_counter = n
            except ValueError:
                pass

        f_node = FunctionNode(f_gui, stable_id=stable_id)
        self.functions_nodes.append(f_node)
        return f_node

    def _function_node_by_stable_id(self, stable_id: str) -> FunctionNode:
        for fn in self.functions_nodes:
            if fn.stable_id == stable_id:
                return fn
        raise ValueError(f"No function node with stable_id {stable_id!r}")

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

        # 7. Check that output and input types are compatible
        from fiatlight.fiat_types.type_compat import is_link_compatible, explain_incompatibility

        src_output_gui = src_function_node.function_with_gui.output(src_output_idx)
        dst_input_gui = dst_function_node.function_with_gui.input(dst_input_name)
        src_type = src_output_gui._type
        dst_type = dst_input_gui._type
        if src_type is not None and dst_type is not None:
            if not is_link_compatible(src_type, dst_type):
                return False, explain_incompatibility(src_type, dst_type)

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
        src_function: str | Function | FunctionWithGui | FunctionNode,
        dst_function: str | Function | FunctionWithGui | FunctionNode,
        dst_input_name: str | None = None,
        src_output_idx: int = 0,
    ) -> None:
        """Connect a source function's output to a destination function's input.

        Each endpoint can be addressed in any of these ways:

        - **As a string**: matches the node's `label` (the display name) or,
          failing that, the function's name. So if you wrote
          `graph.add_function(cos, label="cos1")`, you can use `"cos1"`.
          When the same function is added several times with the same label
          (or no label), the string is ambiguous and `add_link` raises —
          use a node handle instead (see below).
        - **As a node handle**: the `FunctionNode` returned by
          `add_function` / `add_gui_node` / etc. Always unambiguous, so this
          is what to use when the same function appears twice in the graph.
        - **As the original Python callable** or a `FunctionWithGui`
          instance: matched by identity.

        Examples:

            n_a = graph.add_function(load_image)
            n_b = graph.add_function(blur)
            graph.add_link(n_a, n_b)
            graph.add_link("load_image", "blur")     # equivalent

            # Same function used twice — pass handles to disambiguate.
            cos1 = graph.add_function(cos, label="cos1")
            cos2 = graph.add_function(cos, label="cos2")
            graph.add_link(cos1, cos2)
            graph.add_link("cos1", "cos2")           # also works (label match)

        `dst_input_name` defaults to the destination's first input name;
        `src_output_idx` defaults to 0.
        """
        src_function_node = self._function_node_with_name_or_is_function(src_function)
        dst_function_node = self._function_node_with_name_or_is_function(dst_function)
        self._add_link_from_function_nodes(
            src_function_node, dst_function_node, dst_input_name=dst_input_name, src_output_idx=src_output_idx
        )

    def merge_graph(self, other: "FunctionsGraph") -> None:
        """Merge another FunctionsGraph into this one"""
        # Re-mint stable ids on incoming nodes; otherwise their counters
        # collide with this graph's.
        for fn_node in other.functions_nodes:
            fn_node.stable_id = self._next_stable_id()
        self.functions_nodes.extend(other.functions_nodes)
        self.functions_nodes_links.extend(other.functions_nodes_links)

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
        self, name_or_function: str | Function | FunctionWithGui | FunctionNode
    ) -> FunctionNode:
        """Resolve any of the four endpoint forms accepted by `add_link`
        (string, node handle, FunctionWithGui, raw callable) to a
        FunctionNode in this graph. See `add_link` for the user-facing
        contract; this method centralises the matching logic so all the
        addressing forms behave consistently."""
        if isinstance(name_or_function, FunctionNode):
            if name_or_function in self.functions_nodes:
                return name_or_function
            raise ValueError(f"FunctionNode {name_or_function.stable_id!r} not in this graph")

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

    def _function_node_with_name(self, name_or_label: str) -> FunctionNode:
        """Look up a node by string. Matches against the node's label
        (typically the user-set display name) or, failing that, the
        wrapped function's name.

        A single node may match through both fields (default case: label
        defaults to function_name) — that's still one match, not two. The
        ambiguous case is when *different* nodes match the same string;
        callers must pass a `FunctionNode` handle in that case (see the
        `add_link` docstring for examples).
        """
        matches: List[FunctionNode] = []
        for fn in self.functions_nodes:
            if fn.function_with_gui.label == name_or_label or fn.function_with_gui.function_name == name_or_label:
                matches.append(fn)
        # A node can satisfy both predicates (label == function_name); dedup.
        unique = list({id(fn): fn for fn in matches}.values())
        if len(unique) == 0:
            raise ValueError(f"No function node matches {name_or_label!r} (tried label and function_name).")
        if len(unique) > 1:
            raise ValueError(
                f"{len(unique)} nodes match {name_or_label!r}. Capture the FunctionNode "
                "returned by add_function and pass that handle to add_link instead."
            )
        return unique[0]

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

    def save_workspace_core_to_json(self) -> JsonDict:
        """Serialize the parts of the workspace that don't depend on the GUI
        layer: an id-keyed `nodes` dict carrying each function's identity,
        input values, and per-pin GUI option blobs, plus a `links` list that
        references nodes by stable id.

        Positions and expand flags live in `FunctionsGraphGui` and are added
        on top of this dict by `FunctionsGraphGui.save_workspace_to_json`.
        The top-level `version` is also added by the caller.
        """
        nodes: JsonDict = {}
        for fn in self.functions_nodes:
            f_gui = fn.function_with_gui
            gui_opts = f_gui.save_gui_options_to_json()
            entry: JsonDict = {
                "function_ref": f_gui.function_ref,
                "function_name": f_gui.function_name,
                "input_values": fn.save_user_inputs_to_json(),
                "input_gui_options": gui_opts.get("inputs", {}),
                "output_gui_options": gui_opts.get("outputs", {}),
            }
            internal = gui_opts.get("internal_gui_options")
            if internal is not None:
                entry["internal_gui_options"] = internal
            nodes[fn.stable_id] = entry

        links: List[JsonDict] = []
        for link in self.functions_nodes_links:
            links.append(
                {
                    "src_node": link.src_function_node.stable_id,
                    "src_output_idx": link.src_output_idx,
                    "dst_node": link.dst_function_node.stable_id,
                    "dst_input_name": link.dst_input_name,
                }
            )
        return {"nodes": nodes, "links": links}

    def load_workspace_core_from_json(
        self,
        json_data: JsonDict,
        function_factory_from_ref: FunctionWithGuiFactoryFromName,
        *,
        rebuild_topology: bool = True,
    ) -> None:
        """Restore a graph from the core JSON written by
        `save_workspace_core_to_json`.

        With ``rebuild_topology=True`` (the default, for graphs the user
        edits in the GUI) the existing nodes/links are wiped and the saved
        ones are recreated, looking each function up via
        ``function_factory_from_ref``.

        With ``rebuild_topology=False`` (programmatic graphs whose shape
        comes from Python code), the existing nodes are kept; only their
        values and GUI option blobs are restored, matched by stable_id.

        Saved nodes whose function_ref is no longer registered are skipped
        with a warning, and any link that touches a missing endpoint is
        dropped — load is best-effort, never raises on a single bad node.
        """
        import logging

        if rebuild_topology:
            self.functions_nodes = []
            self.functions_nodes_links = []
            self._stable_id_counter = 0

        nodes_data = json_data.get("nodes", {})
        for stable_id, node_data in nodes_data.items():
            if rebuild_topology:
                function_ref = node_data.get("function_ref", "")
                try:
                    f_gui = function_factory_from_ref(function_ref)
                except ValueError as e:
                    logging.warning(f"Workspace: skipping node {stable_id!r}: {e}")
                    continue
                saved_name = node_data.get("function_name")
                if saved_name:
                    f_gui.function_name = saved_name
                f_node = self._add_function_with_gui(f_gui, stable_id=stable_id)
            else:
                try:
                    f_node = self._function_node_by_stable_id(stable_id)
                except ValueError:
                    logging.warning(
                        f"Workspace: saved node {stable_id!r} has no match in code-defined graph; ignoring."
                    )
                    continue
                f_gui = f_node.function_with_gui

            self._restore_node_payload(f_node, f_gui, node_data)

        if rebuild_topology:
            self._restore_links_from_workspace(json_data.get("links", []))

    @staticmethod
    def _restore_node_payload(f_node: FunctionNode, f_gui: FunctionWithGui, node_data: JsonDict) -> None:
        import logging

        try:
            f_node.load_user_inputs_from_json(node_data.get("input_values", {}))
        except Exception as e:
            logging.warning(f"Workspace: error restoring input values for {f_node.stable_id!r}: {e}")
        gui_payload: JsonDict = {
            "inputs": node_data.get("input_gui_options", {}),
            "outputs": node_data.get("output_gui_options", {}),
        }
        if "internal_gui_options" in node_data:
            gui_payload["internal_gui_options"] = node_data["internal_gui_options"]
        try:
            f_gui.load_gui_options_from_json(gui_payload)
        except Exception as e:
            logging.warning(f"Workspace: error restoring gui options for {f_node.stable_id!r}: {e}")

    def _restore_links_from_workspace(self, links_data: List[JsonDict]) -> None:
        import logging

        for link_data in links_data:
            src_id = link_data.get("src_node")
            dst_id = link_data.get("dst_node")
            try:
                src_node = self._function_node_by_stable_id(src_id) if src_id else None
                dst_node = self._function_node_by_stable_id(dst_id) if dst_id else None
            except ValueError as e:
                logging.warning(f"Workspace: link {src_id!r} -> {dst_id!r} skipped: {e}")
                continue
            if src_node is None or dst_node is None:
                logging.warning(f"Workspace: link {src_id!r} -> {dst_id!r} skipped: missing endpoint id")
                continue
            try:
                self._add_link_from_function_nodes(
                    src_node,
                    dst_node,
                    dst_input_name=link_data.get("dst_input_name"),
                    src_output_idx=link_data.get("src_output_idx", 0),
                )
            except ValueError as e:
                logging.warning(f"Workspace: link {src_id!r} -> {dst_id!r} rejected: {e}")
