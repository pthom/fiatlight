from __future__ import annotations
from fiatlight.functions_graph import FunctionsGraph, FunctionsLink
from fiatlight.function_node_gui import FunctionNodeGui
from imgui_bundle import imgui, imgui_node_editor as ed, hello_imgui, ImVec2
from typing import List


class FunctionsLinkGui:
    function_link: FunctionsLink
    link_id: ed.LinkId
    start_id: ed.PinId
    end_id: ed.PinId

    def __init__(self, function_link: FunctionsLink, function_nodes: List[FunctionNodeGui]) -> None:
        self.function_link = function_link
        self.link_id = ed.LinkId.create()
        for f in function_nodes:
            if f.function == function_link.source:
                self.start_id = f.pins_output[function_link.source_output_id]
            if f.function == function_link.target:
                self.end_id = f.pins_input[function_link.target_input_id]
        assert hasattr(self, "start_id")
        assert hasattr(self, "end_id")

    def draw(self) -> None:
        ed.link(self.link_id, self.start_id, self.end_id)


class FunctionsGraphGui:
    functions_graph: FunctionsGraph

    function_nodes_gui: List[FunctionNodeGui]
    functions_links_gui: List[FunctionsLinkGui]

    shall_layout_graph: bool = False

    _idx_frame: int = 0

    def __init__(self, functions_graph: FunctionsGraph) -> None:
        self.functions_graph = functions_graph

        self.function_nodes_gui = []
        for f in self.functions_graph.functions:
            self.function_nodes_gui.append(FunctionNodeGui(f))

        self.functions_links_gui = []
        for link in self.functions_graph.links:
            link_gui = FunctionsLinkGui(link, self.function_nodes_gui)
            self.functions_links_gui.append(link_gui)

    def _layout_graph_if_required(self) -> None:
        def are_all_nodes_on_zero() -> bool:
            # the node sizes are not set yet in the first frame
            # we need to wait until we know them
            if self._idx_frame == 0:
                return False

            for node in self.function_nodes_gui:
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

            for i, fn in enumerate(self.function_nodes_gui):
                ed.set_node_position(fn.node_id, current_position)
                node_size = ed.get_node_size(fn.node_id)
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
                fn.draw_node()
                imgui.pop_id()

        def draw_links() -> None:
            for fn in self.function_nodes_gui:
                pass

        self._layout_graph_if_required()
        imgui.push_id(str(id(self)))
        ed.begin("FunctionsGraphGui")
        draw_nodes()
        draw_links()
        ed.end()
        imgui.pop_id()
        self._idx_frame += 1


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

    fgg = FunctionsGraphGui(fg)

    from imgui_bundle import immapp

    def gui() -> None:
        fgg.draw()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
