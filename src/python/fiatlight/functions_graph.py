from __future__ import annotations
from fiatlight.functions_node import FunctionNode
from fiatlight.function_with_gui import FunctionWithGui
from imgui_bundle import imgui, imgui_node_editor as ed, hello_imgui, ImVec2
from typing import List, Any, Sequence


class FunctionsGraph:
    function_nodes: List[FunctionNode]
    shall_layout_graph: bool = False

    _idx_frame: int = 0

    def __init__(self, functions: Sequence[FunctionWithGui]) -> None:
        assert len(functions) > 0
        self.function_nodes = []
        for f in functions:
            self.function_nodes.append(FunctionNode(f))

        for i in range(len(self.function_nodes) - 1):
            fn0 = self.function_nodes[i]
            fn1 = self.function_nodes[i + 1]
            fn0.next_function_node = fn1

    def set_input(self, input: Any) -> None:
        self.function_nodes[0].set_input(input)

    def _layout_graph_if_required(self) -> None:
        def are_all_nodes_on_zero() -> bool:
            # the node sizes are not set yet in the first frame
            # we need to wait until we know them
            if self._idx_frame == 0:
                return False

            for node in self.function_nodes:
                pos = ed.get_node_position(node.node_id)
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

            for i, fn in enumerate(self.function_nodes):
                ed.set_node_position(fn.node_id, current_position)
                node_size = ed.get_node_size(fn.node_id)
                current_position.x += node_size.x + width_between_nodes
                current_row_height = max(current_row_height, node_size.y)
                if current_position.x + node_size.x > w:
                    current_position.x = 0
                    current_position.y += current_row_height + height_between_nodes
                    current_row_height = 0

    def draw(self) -> None:
        self._layout_graph_if_required()
        imgui.push_id(str(id(self)))

        ed.begin("FunctionsGraph")
        # draw function nodes
        for fn in self.function_nodes:
            imgui.push_id(str(id(fn)))
            fn.draw_node()
            imgui.pop_id()
        # Note: those loops shall not be merged
        for fn in self.function_nodes:
            fn.draw_link()
        ed.end()

        imgui.pop_id()
        self._idx_frame += 1
