from __future__ import annotations
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import FunctionWithGui
from fiatlight.config import config
from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, ImVec2, immapp
from typing import List, Optional, Any, Sequence
import traceback
import sys


class FunctionsCompositionGraph:
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


class FunctionNode:
    function: FunctionWithGui
    next_function_node: Optional[FunctionNode]
    input_data_with_gui: AnyDataWithGui
    output_data_with_gui: AnyDataWithGui

    last_exception_message: Optional[str] = None
    last_exception_traceback: Optional[str] = None

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

        # self.observer = observer

    def _draw_exception_message(self) -> None:
        # return
        if self.last_exception_message is None:
            return
        imgui.text_colored(config.colors.error, self.last_exception_message)

    def draw_node(self, idx: int) -> None:
        assert self.function is not None

        ed.begin_node(self.node_id)
        position = ed.get_node_position(self.node_id)
        if position.x == 0 and position.y == 0:
            nb_nodes_per_row = 5
            width_between_nodes = immapp.em_size(20)
            height_between_nodes = immapp.em_size(20)
            position = ImVec2(
                (idx % nb_nodes_per_row) * width_between_nodes, (idx // nb_nodes_per_row) * height_between_nodes
            )
            ed.set_node_position(self.node_id, position)

        id_fn = str(id(self.function))
        imgui.push_id(id_fn)

        imgui.text(self.function.name())
        self._draw_exception_message()

        params_changed = self.function.gui_params()
        if params_changed:
            self._invoke_function()
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

    def _invoke_function(self) -> Any:
        input_data = self.input_data_with_gui.get()
        if self.function is not None:
            try:
                r = self.function.f(input_data)
                self.last_exception_message = None
                self.last_exception_traceback = None
            except Exception as e:
                self.last_exception_message = str(e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
                self.last_exception_traceback = "".join(traceback_details)
                r = None

            self.output_data_with_gui.set(r)
            if self.next_function_node is not None:
                self.next_function_node.set_input(r)

    def set_input(self, input_data: Any) -> None:
        self.input_data_with_gui.set(input_data)
        self._invoke_function()
