from __future__ import annotations
from fiatlight.functions_node import FunctionNode
from fiatlight.function_with_gui import FunctionWithGui
from imgui_bundle import imgui, imgui_node_editor as ed
from typing import List, Any, Sequence


class FunctionsGraph:
    function_nodes: List[FunctionNode]

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

    def draw(self) -> None:
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
