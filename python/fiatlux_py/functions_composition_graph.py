from __future__ import annotations
from fiatlux_py.any_data_with_gui import AnyDataWithGui
from fiatlux_py.function_with_gui import FunctionWithGui
from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, ImVec2
from typing import List, Optional, Any, Sequence


class FunctionsCompositionGraph:
    function_nodes: List[_FunctionNode]

    def __init__(self, functions: Sequence[FunctionWithGui]) -> None:
        assert len(functions) > 0
        f0 = functions[0]

        input_fake_function = _InputWithGui()
        input_fake_function.input_gui = f0.input_gui
        input_fake_function.output_gui = f0.input_gui

        input_node = _FunctionNode(input_fake_function)
        self.function_nodes = []
        self.function_nodes.append(input_node)

        for f in functions:
            self.function_nodes.append(_FunctionNode(f))

        for i in range(len(self.function_nodes) - 1):
            fn0 = self.function_nodes[i]
            fn1 = self.function_nodes[i + 1]
            fn0.next_function_node = fn1

    def set_input(self, input: Any) -> None:
        self.function_nodes[0].set_input(input)

    def draw(self) -> None:
        imgui.push_id(str(id(self)))

        ed.begin("FunctionsCompositionGraph")
        # draw function nodes
        for i, fn in enumerate(self.function_nodes):
            fn.draw_node(idx=i)
        # Note: those loops shall not be merged
        for fn in self.function_nodes:
            fn.draw_link()
        ed.end()

        imgui.pop_id()


class _InputWithGui(FunctionWithGui):
    def f(self, x: Any) -> Any:
        return x

    def gui_params(self) -> bool:
        return False

    def name(self) -> str:
        return "Input"


class _FunctionNode:
    function: FunctionWithGui
    next_function_node: Optional[_FunctionNode]
    input_data_with_gui: AnyDataWithGui
    output_data_with_gui: AnyDataWithGui

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    def __init__(self, function: FunctionWithGui) -> None:
        self.function = function
        self.next_function_node = None
        self.input_data_with_gui = function.input_gui
        self.output_data_with_gui = function.output_gui

        self.node_id = ed.NodeId.create()
        self.pin_input = ed.PinId.create()
        self.pin_output = ed.PinId.create()
        self.link_id = ed.LinkId.create()

    def draw_node(self, idx: int) -> None:
        assert self.function is not None

        ed.begin_node(self.node_id)
        position = ed.get_node_position(self.node_id)
        if position.x == 0 and position.y == 0:
            width_between_nodes = 200
            position = ImVec2(idx * width_between_nodes + 1, 0)  # type: ignore
            ed.set_node_position(self.node_id, position)

        imgui.text(self.function.name())

        id_fn = str(id(self.function))
        imgui.push_id(id_fn)

        params_changed = self.function.gui_params()
        if params_changed:
            if self.input_data_with_gui.get() is not None and self.function is not None:
                r = self.function.f(self.input_data_with_gui.get())
                self.output_data_with_gui.set(r)
                if self.next_function_node is not None:
                    self.next_function_node.set_input(r)
        imgui.pop_id()

        draw_input_pin = idx != 0
        if draw_input_pin:
            ed.begin_pin(self.pin_input, ed.PinKind.input)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()

        draw_input_set_data = idx == 0
        if draw_input_set_data:
            new_value = self.input_data_with_gui.gui_set_input()
            if new_value is not None:
                self.set_input(new_value)

        def draw_output() -> None:
            if self.output_data_with_gui.get() is None:
                imgui.text("None")
            else:
                imgui.push_id(str(id(self.output_data_with_gui)))
                imgui.begin_group()
                self.output_data_with_gui.gui_data(function_name=self.function.name())
                imgui.pop_id()
                imgui.end_group()
            imgui.same_line()
            ed.begin_pin(self.pin_output, ed.PinKind.output)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()

        draw_output()

        ed.end_node()

    def draw_link(self) -> None:
        if self.next_function_node is None:
            return
        ed.link(self.link_id, self.pin_output, self.next_function_node.pin_input)

    def set_input(self, input_data: Any) -> None:
        self.input_data_with_gui.set(input_data)
        if self.function is not None:
            r = self.function.f(input_data)
            self.output_data_with_gui.set(r)
            if self.next_function_node is not None:
                self.next_function_node.set_input(r)
