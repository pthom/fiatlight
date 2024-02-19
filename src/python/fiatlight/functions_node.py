from __future__ import annotations
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import FunctionWithGui
from fiatlight.config import config
from fiatlight.internal import fl_widgets
from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, ImVec2, immapp, imgui_ctx
from typing import Optional, Any
import traceback
import sys


class FunctionNode:
    function: FunctionWithGui
    next_function_node: Optional[FunctionNode]
    input_data_with_gui: AnyDataWithGui | None
    output_data_with_gui: AnyDataWithGui | None

    last_exception_message: Optional[str] = None
    last_exception_traceback: Optional[str] = None

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    node_size: ImVec2  # will be set after the node is drawn once

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
        fl_widgets.text("Exception:\n" + self.last_exception_message, max_line_width=30, color=config.colors.error)

    def old_draw_node(self, idx: int) -> None:
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

        imgui.text(self.function.name())
        self._draw_exception_message()

        params_changed = self.function.gui_params()
        if params_changed:
            self._invoke_function()

        draw_input_pin = idx != 0
        if draw_input_pin:
            ed.begin_pin(self.pin_input, ed.PinKind.input)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()

        def draw_output() -> None:
            if self.output_data_with_gui is None:
                return
            if self.output_data_with_gui.get() is None:
                imgui.text("None")
            else:
                imgui.push_id(str(id(self.output_data_with_gui)))
                imgui.begin_group()
                self.output_data_with_gui.gui_present()
                imgui.pop_id()
                imgui.end_group()
            imgui.same_line()
            ed.begin_pin(self.pin_output, ed.PinKind.output)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()

        draw_output()

        ed.end_node()

    def draw_node(self) -> None:
        def draw_title() -> None:
            imgui.text(self.function.name())

        def draw_exception_message() -> None:
            last_exception_message = self.last_exception_message
            if last_exception_message is None:
                return
            fl_widgets.text("Exception:\n" + last_exception_message, max_line_width=30, color=config.colors.error)

        def draw_input_pin() -> None:
            if self.input_data_with_gui is None:
                return
            ed.begin_pin(self.pin_input, ed.PinKind.input)
            imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_LEFT)
            if self.input_data_with_gui.value is None:
                imgui.same_line()
                imgui.text("No input")
            ed.end_pin()

        def draw_function_output() -> None:
            if self.output_data_with_gui is None:
                return
            with imgui_ctx.push_id("output"):
                output = self.output_data_with_gui.value
                if output is None:
                    imgui.text("None")
                else:
                    self.output_data_with_gui.gui_present()

        def draw_output_pin() -> None:
            if hasattr(self, "node_size"):
                imgui.same_line(self.node_size.x - immapp.em_size(2))
                ed.begin_pin(self.pin_output, ed.PinKind.output)
                imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_RIGHT)
                ed.end_pin()

        def edit_params() -> bool:
            from imgui_bundle import imgui_ctx

            changed = False
            if self.function.parameters_with_gui is not None:
                for param in self.function.parameters_with_gui:
                    with imgui_ctx.push_obj_id(param):
                        if param.edit_gui is not None:
                            imgui.text(param.name + ":")
                            changed = param.edit_gui() or changed
            return changed

        ed.begin_node(self.node_id)
        draw_title()
        draw_input_pin()
        draw_output_pin()
        draw_exception_message()
        if edit_params():
            self._invoke_function()
        draw_function_output()
        ed.end_node()
        self.node_size = imgui.get_item_rect_size()

    def draw_link(self) -> None:
        if self.next_function_node is None:
            return
        ed.link(self.link_id, self.pin_output, self.next_function_node.pin_input)

    def _invoke_function(self) -> Any:
        if self.input_data_with_gui is None or self.output_data_with_gui is None:
            return
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
        if self.input_data_with_gui is None:
            return
        self.input_data_with_gui.set(input_data)
        self._invoke_function()
