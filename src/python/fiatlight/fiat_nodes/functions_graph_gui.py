from __future__ import annotations

import logging

from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui, FunctionNode
from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui, FunctionNodeLinkGui
from imgui_bundle import imgui, imgui_node_editor as ed, hello_imgui, ImVec2, imgui_ctx
from typing import List, Dict


class FunctionsGraphGui:
    functions_graph: FunctionsGraph

    function_nodes_gui: List[FunctionNodeGui]
    functions_links_gui: List[FunctionNodeLinkGui]

    shall_layout_graph: bool = False

    _idx_frame: int = 0

    def __init__(self, functions_graph: FunctionsGraph) -> None:
        self.functions_graph = functions_graph

        self.function_nodes_gui = []
        for f in self.functions_graph.functions_nodes:
            self.function_nodes_gui.append(FunctionNodeGui(f))

        self.functions_links_gui = []
        for link in self.functions_graph.functions_nodes_links:
            link_gui = FunctionNodeLinkGui(link, self.function_nodes_gui)
            self.functions_links_gui.append(link_gui)

    def add_function_with_gui(self, function: FunctionWithGui) -> None:
        function_node = FunctionNode(function)
        function_node_gui = FunctionNodeGui(function_node)
        self.function_nodes_gui.append(function_node_gui)

    def _layout_graph_if_required(self) -> None:
        def are_all_nodes_on_zero() -> bool:
            # the node sizes are not set yet in the first frame
            # we need to wait until we know them
            if self._idx_frame == 0:
                return False

            for node in self.function_nodes_gui:
                pos = ed.get_node_position(node.node_id())
                if pos.x != 0 or pos.y != 0:
                    return False
            return True

        if self.shall_layout_graph or are_all_nodes_on_zero():
            self.shall_layout_graph = False
            width_between_nodes = hello_imgui.em_size(4)
            height_between_nodes = hello_imgui.em_size(4)
            current_row_height = 0.0
            w = imgui.get_window_width()
            current_position = ImVec2(0, 0)

            for i, fn in enumerate(self.function_nodes_gui):
                ed.set_node_position(fn.node_id(), current_position)
                node_size = ed.get_node_size(fn.node_id())
                current_position.x += node_size.x + width_between_nodes
                current_row_height = max(current_row_height, node_size.y)
                if current_position.x + node_size.x > w:
                    current_position.x = 0
                    current_position.y += current_row_height + height_between_nodes
                    current_row_height = 0

    def draw(self) -> None:
        def draw_nodes() -> None:
            for fn in self.function_nodes_gui:
                imgui.push_id(str(id(fn)))
                fn.draw_node(self.functions_graph.function_node_unique_name(fn._function_node))  # noqa
                imgui.pop_id()

        def draw_links() -> None:
            for link in self.functions_links_gui:
                link.draw()

        self._layout_graph_if_required()
        with imgui_ctx.push_obj_id(self):
            ed.begin("FunctionsGraphGui")
            draw_nodes()
            draw_links()
            self._handle_links_edit()
            ed.end()
        self._idx_frame += 1

    def _handle_links_edit(self) -> None:
        # Handle creation action, returns true if editor want to create new object (node or link)
        if ed.begin_create():
            input_pin_id = ed.PinId()
            output_pin_id = ed.PinId()

            # QueryNewLink returns true if editor want to create new link between pins.
            if ed.query_new_link(input_pin_id, output_pin_id):
                # Link can be created only for two valid pins, it is up to you to
                # validate if connection make sense. Editor is happy to make any.
                #
                # Link always goes from input to output. User may choose to drag
                # link from output pin or input pin. This determines which pin ids
                # are valid and which are not:
                #   * input valid, output invalid - user started to drag new link from input pin
                #   * input invalid, output valid - user started to drag new link from output pin
                #   * input valid, output valid   - user dragged link over other pin, can be validated

                if input_pin_id and output_pin_id:  # both are valid, let's accept link
                    # ed.AcceptNewItem(): return true when user release mouse button.
                    if ed.accept_new_item():
                        self._try_add_link(input_pin_id, output_pin_id)
            ed.end_create()

    def _try_add_link(self, input_pin_id: ed.PinId, output_pin_id: ed.PinId) -> None:
        # We need to add
        # - a link to self.functions_graph.functions_nodes_links
        # - and a link to self.functions_links_gui
        logging.warning("Work in progress")

    def function_node_unique_name(self, function_node_gui: FunctionNodeGui) -> str:
        return self.functions_graph.function_node_unique_name(function_node_gui._function_node)  # noqa

    def function_node_with_unique_name(self, function_name: str) -> FunctionNodeGui:
        return next(fn for fn in self.function_nodes_gui if self.function_node_unique_name(fn) == function_name)

    def all_function_nodes_with_unique_names(self) -> Dict[str, FunctionNodeGui]:
        return {self.function_node_unique_name(fn): fn for fn in self.function_nodes_gui}

    def save_user_inputs_to_json(self) -> JsonDict:
        function_graph_dict = self.functions_graph.save_user_inputs_to_json()

        function_gui_settings_dict = {}
        for name, fn in self.all_function_nodes_with_unique_names().items():
            function_gui_settings_dict[name] = fn.save_gui_options_to_json()

        r = {
            "functions_graph": function_graph_dict,
            "functions_gui_settings": function_gui_settings_dict,
        }
        return r

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        self.functions_graph.load_user_inputs_from_json(json_data["functions_graph"])

        if "functions_gui_settings" in json_data:
            function_gui_settings_dict = json_data["functions_gui_settings"]
            for name, fn in self.all_function_nodes_with_unique_names().items():
                if name in function_gui_settings_dict:
                    fn.load_gui_options_from_json(function_gui_settings_dict[name])


def sandbox() -> None:
    def add(a: int, b: int = 2) -> int:
        return a + b

    def mul2(x: int) -> int:
        return x * 2

    def div3(x: int) -> float:
        return x / 3

    fg = FunctionsGraph.from_function_composition([add, mul2, div3])
    fgg = FunctionsGraphGui(fg)

    from imgui_bundle import immapp

    def gui() -> None:
        fgg.draw()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
