from __future__ import annotations
from fiatlight.function_node import FunctionNode, FunctionNodeLink
from fiatlight.internal.fl_widgets import draw_node_gui_right_align
from fiatlight.config import config
from fiatlight.internal import fl_widgets
from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, ImVec2, imgui_ctx, hello_imgui
from typing import Dict, List


class FunctionNodeLinkGui:
    function_node_link: FunctionNodeLink
    link_id: ed.LinkId
    start_id: ed.PinId
    end_id: ed.PinId

    def __init__(self, function_node_link: FunctionNodeLink, function_nodes: List[FunctionNodeGui]) -> None:
        self.function_node_link = function_node_link
        self.link_id = ed.LinkId.create()
        for f in function_nodes:
            if f.function_node.function_with_gui == function_node_link.src_function_node.function_with_gui:
                self.start_id = f.pins_output[function_node_link.src_output_name]
            if f.function_node.function_with_gui == function_node_link.dst_function_node.function_with_gui:
                self.end_id = f.pins_input[function_node_link.dst_input_name]
        assert hasattr(self, "start_id")
        assert hasattr(self, "end_id")

    def draw(self) -> None:
        ed.link(self.link_id, self.start_id, self.end_id)


class FunctionNodeGui:
    function_node: FunctionNode

    node_id: ed.NodeId
    pins_input: Dict[str, ed.PinId]
    pins_output: Dict[str, ed.PinId]

    node_size: ImVec2 | None = None  # will be set after the node is drawn once
    _first_frame = True

    def __init__(self, function_node: FunctionNode) -> None:
        self.function_node = function_node

        self.node_id = ed.NodeId.create()

        self.pins_input = {}
        for input_with_gui in self.function_node.function_with_gui.inputs_with_gui:
            self.pins_input[input_with_gui.name] = ed.PinId.create()

        self.pins_output = {}
        for output_with_gui in self.function_node.function_with_gui.outputs_with_gui:
            self.pins_output[output_with_gui.name] = ed.PinId.create()

    def draw_node(self) -> None:
        def draw_title() -> None:
            fl_widgets.text_custom(self.function_node.name)

        def draw_exception_message() -> None:
            last_exception_message = self.function_node.function_with_gui.last_exception_message
            if last_exception_message is None:
                return

            min_exception_width = hello_imgui.em_size(12)
            exception_width = min_exception_width
            if self.node_size is not None:
                exception_width = self.node_size.x - hello_imgui.em_size(2)
                if exception_width < min_exception_width:
                    exception_width = min_exception_width
            fl_widgets.text_custom(
                "Exception:\n" + last_exception_message, max_width_pixels=exception_width, color=config.colors.error
            )

        def draw_input_pins() -> None:
            for name, pin_input in self.pins_input.items():
                ed.begin_pin(pin_input, ed.PinKind.input)
                imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_LEFT + " " + name)
                ed.end_pin()

        def draw_output_pins() -> None:
            def draw() -> None:
                for name, pin_output in self.pins_output.items():
                    ed.begin_pin(pin_output, ed.PinKind.output)
                    if len(self.function_node.function_with_gui.outputs_with_gui) > 1:
                        imgui.text(name + " " + icons_fontawesome.ICON_FA_ARROW_CIRCLE_RIGHT)
                    else:
                        imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_RIGHT)
                    ed.end_pin()

            draw_node_gui_right_align(self.node_id, draw)

        def draw_function_outputs() -> None:
            for output_param in self.function_node.function_with_gui.outputs_with_gui:
                with imgui_ctx.push_obj_id(output_param):
                    if len(self.function_node.function_with_gui.outputs_with_gui) > 1:
                        fl_widgets.text_custom(output_param.name + ":")
                    if output_param.parameter_with_gui.value is None:
                        imgui.text("None")
                    else:
                        output_param.parameter_with_gui.call_gui_present()

        def draw_function_inputs() -> bool:
            changed = False
            if len(self.function_node.function_with_gui.inputs_with_gui) == 0:
                changed = self._first_frame
            for input_param in self.function_node.function_with_gui.inputs_with_gui:
                with imgui_ctx.push_obj_id(input_param):
                    if self.function_node.has_input_link(input_param.name):
                        fl_widgets.text_custom(input_param.name + ":")
                        imgui.same_line()
                        input_param.parameter_with_gui.call_gui_present()
                    else:
                        fl_widgets.text_custom(input_param.name + ":")
                        imgui.same_line()
                        changed = input_param.parameter_with_gui.call_gui_edit() or changed
            return changed

        ed.begin_node(self.node_id)
        draw_title()
        draw_input_pins()
        draw_exception_message()
        if draw_function_inputs():
            self.function_node.invoke_function()
        fl_widgets.node_separator(self.node_id, text="Output")
        draw_function_outputs()
        imgui.new_line()
        draw_output_pins()
        ed.end_node()
        self.node_size = ed.get_node_size(self.node_id)
        self._first_frame = False


def sandbox() -> None:
    from fiatlight.to_gui import any_function_to_function_with_gui
    from imgui_bundle import immapp

    def add(x: int, y: int = 2) -> int:
        return x + y

    function_with_gui = any_function_to_function_with_gui(add)
    function_node = FunctionNode(function_with_gui, name="add")
    function_node_gui = FunctionNodeGui(function_node)

    def gui() -> None:
        ed.begin("Functions Graph")
        function_node_gui.draw_node()
        ed.end()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()