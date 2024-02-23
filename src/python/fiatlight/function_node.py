from __future__ import annotations
from fiatlight.function_with_gui import FunctionWithGui, FunctionParameterWithGui
from fiatlight.internal.fl_widgets import draw_node_gui_right_align
from fiatlight.config import config
from fiatlight.internal import fl_widgets
from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, ImVec2, imgui_ctx, hello_imgui
from typing import Optional, List


class FunctionNode:
    function: FunctionWithGui
    next_function_node: Optional[FunctionNode]

    node_id: ed.NodeId
    pin_input: List[ed.PinId]
    pin_output: List[ed.PinId]
    link_id: ed.LinkId

    node_size: ImVec2 | None = None  # will be set after the node is drawn once

    def __init__(self, function: FunctionWithGui) -> None:
        self.function = function
        self.next_function_node = None

        self.node_id = ed.NodeId.create()

        self.pin_input = []
        for _ in function.inputs_with_gui:
            self.pin_input.append(ed.PinId.create())

        self.pin_output = []
        for _ in function.outputs_with_gui:
            self.pin_output.append(ed.PinId.create())

        self.link_id = ed.LinkId.create()

    def draw_node(self) -> None:
        def draw_title() -> None:
            fl_widgets.text_custom(self.function.name)

        def draw_exception_message() -> None:
            last_exception_message = self.function.last_exception_message
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
            for input_param, pin_input in zip(self.function.inputs_with_gui, self.pin_input):
                ed.begin_pin(pin_input, ed.PinKind.input)
                imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_LEFT + " " + input_param.name)
                ed.end_pin()

        def draw_output_pins() -> None:
            def draw() -> None:
                for output_param, pin_output in zip(self.function.outputs_with_gui, self.pin_output):
                    ed.begin_pin(pin_output, ed.PinKind.output)
                    imgui.text(output_param.name + " " + icons_fontawesome.ICON_FA_ARROW_CIRCLE_RIGHT)
                    ed.end_pin()

            draw_node_gui_right_align(self.node_id, draw)

        def draw_function_outputs() -> None:
            for output_param in self.function.outputs_with_gui:
                with imgui_ctx.push_obj_id(output_param):
                    fl_widgets.text_custom(output_param.name + ":")
                    if output_param.parameter_with_gui.value is None:
                        imgui.text("None")
                    else:
                        output_param.parameter_with_gui.call_gui_present()

        def draw_function_inputs() -> bool:
            changed = False
            for input_param in self.function.inputs_with_gui:
                with imgui_ctx.push_obj_id(input_param):
                    fl_widgets.text_custom(input_param.name + ":")
                    changed = input_param.parameter_with_gui.call_gui_edit() or changed
            return changed

        ed.begin_node(self.node_id)
        draw_title()
        draw_input_pins()
        draw_exception_message()
        if draw_function_inputs():
            self.function.invoke()
        draw_function_outputs()
        draw_output_pins()
        ed.end_node()
        self.node_size = ed.get_node_size(self.node_id)

    def draw_link(self) -> None:
        if self.next_function_node is None:
            return
        # ed.link(self.link_id, self.pin_output, self.next_function_node.pin_input)


def sandbox() -> None:
    from fiatlight.data_presenters import make_int_with_gui
    from imgui_bundle import immapp

    function_with_gui = FunctionWithGui()
    function_with_gui.name = "Add"
    function_with_gui.inputs_with_gui = [
        FunctionParameterWithGui("x", make_int_with_gui(1)),
        FunctionParameterWithGui("y", make_int_with_gui(2)),
    ]
    function_with_gui.outputs_with_gui = [FunctionParameterWithGui("output", make_int_with_gui())]

    def f(x: int, y: int) -> int:
        return x + y

    function_with_gui.f_impl = f

    function_node = FunctionNode(function_with_gui)

    def gui() -> None:
        ed.begin("Functions Graph")
        function_node.draw_node()
        ed.end()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
