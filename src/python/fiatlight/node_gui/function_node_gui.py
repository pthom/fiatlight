from __future__ import annotations
from fiatlight.core import FunctionNode, FunctionNodeLink, UnspecifiedValue, OutputWithGui
from fiatlight import widgets
from fiatlight.widgets import IconsFontAwesome6
from imgui_bundle import imgui, imgui_node_editor as ed, ImVec2, imgui_ctx, hello_imgui
from typing import Dict, List, Any


class FunctionNodeLinkGui:
    """The GUI representation as a visual link for a FunctionNodeLink"""

    function_node_link: FunctionNodeLink
    link_id: ed.LinkId
    start_id: ed.PinId
    end_id: ed.PinId

    def __init__(self, function_node_link: FunctionNodeLink, function_nodes: List[FunctionNodeGui]) -> None:
        self.function_node_link = function_node_link
        self.link_id = ed.LinkId.create()
        for f in function_nodes:
            if f.function_node.function_with_gui == function_node_link.src_function_node.function_with_gui:
                self.start_id = f.pins_output[function_node_link.src_output_idx]
            if f.function_node.function_with_gui == function_node_link.dst_function_node.function_with_gui:
                self.end_id = f.pins_input[function_node_link.dst_input_name]
        assert hasattr(self, "start_id")
        assert hasattr(self, "end_id")

    def draw(self) -> None:
        ed.link(self.link_id, self.start_id, self.end_id)


class FunctionNodeGui:
    """The GUI representation as a visual node for a FunctionNode"""

    function_node: FunctionNode

    node_id: ed.NodeId
    pins_input: Dict[str, ed.PinId]
    pins_output: Dict[int, ed.PinId]

    node_size: ImVec2 | None = None  # will be set after the node is drawn once

    _MIN_NODE_WIDTH_EM = 6

    def __init__(self, function_node: FunctionNode) -> None:
        self.function_node = function_node

        self.node_id = ed.NodeId.create()

        self.pins_input = {}
        for input_with_gui in self.function_node.function_with_gui.inputs_with_gui:
            self.pins_input[input_with_gui.name] = ed.PinId.create()

        self.pins_output = {}
        for i, output_with_gui in enumerate(self.function_node.function_with_gui.outputs_with_gui):
            self.pins_output[i] = ed.PinId.create()

    def draw_node(self, unique_name: str) -> None:
        def draw_title() -> None:
            fn_name = self.function_node.function_with_gui.name
            widgets.text_maybe_truncated(fn_name)
            if unique_name != fn_name:
                if imgui.is_item_hovered():
                    widgets.osd_widgets.set_tooltip(f" (id: {unique_name})")

            fn_doc = self.function_node.function_with_gui.doc()
            if fn_doc is not None:
                imgui.text(fn_doc)

        def draw_exception_message() -> None:
            from fiatlight.app_runner import FIATLIGHT_GUI_CONFIG

            last_exception_message = self.function_node.function_with_gui.last_exception_message
            if last_exception_message is None:
                return

            min_exception_width = hello_imgui.em_size(12)
            exception_width = min_exception_width
            if self.node_size is not None:
                exception_width = self.node_size.x - hello_imgui.em_size(2)
                if exception_width < min_exception_width:
                    exception_width = min_exception_width
            widgets.text_maybe_truncated(
                "Exception:\n" + last_exception_message,
                max_width_pixels=exception_width,
                color=FIATLIGHT_GUI_CONFIG.colors.error,
            )

        def draw_function_outputs() -> None:
            def draw_output_pin(pin_output: ed.PinId) -> None:
                def draw() -> None:
                    ed.begin_pin(pin_output, ed.PinKind.output)
                    imgui.text(IconsFontAwesome6.ICON_CIRCLE_RIGHT)
                    ed.end_pin()

                widgets.node_utils.draw_node_gui_right_align(self.node_id, draw)

            def draw_output_value(output_idx: int, output_param: OutputWithGui[Any]) -> None:
                if len(self.function_node.function_with_gui.outputs_with_gui) > 1:
                    widgets.text_maybe_truncated(f"Output {output_idx}: ")
                if output_param.data_with_gui.value is None:
                    imgui.text("None")
                else:
                    output_param.data_with_gui.call_gui_present()

            for i, output_param in enumerate(self.function_node.function_with_gui.outputs_with_gui):
                with imgui_ctx.push_obj_id(output_param):
                    draw_output_value(i, output_param)
                    imgui.same_line()
                    draw_output_pin(self.pins_output[i])

        def draw_function_inputs() -> bool:
            changed = False

            def draw_input_pin(name: str, pin_input: ed.PinId) -> None:
                ed.begin_pin(pin_input, ed.PinKind.input)
                imgui.text(IconsFontAwesome6.ICON_CIRCLE_LEFT + " " + name)
                ed.end_pin()

            if len(self.function_node.function_with_gui.inputs_with_gui) > 1:
                widgets.node_utils.node_separator(self.node_id, text="Params")

            for input_param in self.function_node.function_with_gui.inputs_with_gui:
                with imgui_ctx.push_obj_id(input_param):
                    draw_input_pin(input_param.name, self.pins_input[input_param.name])
                    imgui.same_line()
                    if not self.function_node.has_input_link(input_param.name):
                        imgui.begin_group()
                        changed = input_param.data_with_gui.call_gui_edit() or changed
                        if (
                            input_param.data_with_gui.value is UnspecifiedValue
                            and input_param.default_value is not UnspecifiedValue
                        ):
                            try:
                                default_str = str(input_param.default_value)
                            except Exception:
                                default_str = "???"
                            widgets.text_maybe_truncated(f"(Default: {default_str})", max_width_chars=40, max_lines=3)
                        imgui.end_group()
                    else:
                        imgui.new_line()
            return changed

        ed.begin_node(self.node_id)
        draw_title()
        imgui.dummy(ImVec2(hello_imgui.em_size(self._MIN_NODE_WIDTH_EM), 1))
        if draw_function_inputs():
            self.function_node.invoke_function()
        draw_exception_message()
        output_separator_str = "Outputs" if len(self.function_node.function_with_gui.outputs_with_gui) > 1 else "Output"
        widgets.node_utils.node_separator(self.node_id, text=output_separator_str)
        draw_function_outputs()
        # imgui.new_line()
        ed.end_node()
        self.node_size = ed.get_node_size(self.node_id)


def sandbox() -> None:
    from fiatlight.core import any_function_to_function_with_gui
    from imgui_bundle import immapp

    def add(x: int, y: int = 2) -> int:
        return x + y

    function_with_gui = any_function_to_function_with_gui(add)
    function_node = FunctionNode(function_with_gui, name="add")
    function_node_gui = FunctionNodeGui(function_node)

    def gui() -> None:
        ed.begin("Functions Graph")
        function_node_gui.draw_node("add")
        ed.end()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
