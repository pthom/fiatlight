from __future__ import annotations
from fiatlight.functions_node import FunctionNode
from fiatlight.function_with_gui import FunctionWithGui
from imgui_bundle import imgui, imgui_node_editor as ed
from typing import List, Any, Sequence


class FunctionsGraph:
    function_nodes: List[FunctionNode]

    def __init__(self, functions: Sequence[FunctionWithGui]) -> None:
        assert len(functions) > 0
        f0 = functions[0]

        input_fake_function = _InputWithGui()
        input_fake_function.input_gui = f0.input_gui
        input_fake_function.output_gui = f0.input_gui

        input_node = FunctionNode(input_fake_function)
        self.function_nodes = []
        self.function_nodes.append(input_node)

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


class _InputWithGui(FunctionWithGui):
    def f(self, x: Any) -> Any:
        return x

    def old_gui_params(self) -> bool:
        return False

    def name(self) -> str:
        return "Input"
