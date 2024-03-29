from __future__ import annotations
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import FunctionWithGui, SourceWithGui, Input, Output
from fiatlight.config import config
from fiatlight.internal import fl_widgets
from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, ImVec2, immapp, imgui_ctx, hello_imgui
from typing import Optional, Any, Generic
import traceback
import sys


class FunctionNode(Generic[Input, Output]):
    function: FunctionWithGui[Input, Output]
    next_function_node: Optional[FunctionNode[Output, Any]]
    input_data_with_gui: AnyDataWithGui | None
    output_data_with_gui: AnyDataWithGui | None

    last_exception_message: Optional[str] = None
    last_exception_traceback: Optional[str] = None

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    node_size: ImVec2  # will be set after the node is drawn once

    def __init__(self, function: FunctionWithGui[Input, Output]) -> None:
        self.function = function
        self.next_function_node = None
        self.input_data_with_gui = function.input_gui
        self.output_data_with_gui = function.output_gui

        self.node_id = ed.NodeId.create()
        self.pin_input = ed.PinId.create()
        self.pin_output = ed.PinId.create()
        self.link_id = ed.LinkId.create()

        # self.observer = observer

    def draw_node(self) -> None:
        def draw_title() -> None:
            fl_widgets.text_custom(self.function.name)

        def draw_exception_message() -> None:
            last_exception_message = self.last_exception_message
            if last_exception_message is None:
                return

            min_exception_width = hello_imgui.em_size(12)
            exception_width = min_exception_width
            if hasattr(self, "node_size"):
                exception_width = self.node_size.x - hello_imgui.em_size(2)
                if exception_width < min_exception_width:
                    exception_width = min_exception_width
            fl_widgets.text_custom(
                "Exception:\n" + last_exception_message, max_width_pixels=exception_width, color=config.colors.error
            )

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
                    self.output_data_with_gui.call_gui_present()

        def draw_output_pin() -> None:
            if hasattr(self, "node_size"):
                imgui.same_line(self.node_size.x - immapp.em_size(2.5))
                ed.begin_pin(self.pin_output, ed.PinKind.output)
                imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_RIGHT)
                ed.end_pin()

        def edit_params() -> bool:
            from imgui_bundle import imgui_ctx

            changed = False
            if self.function.parameters_with_gui is not None:
                for param in self.function.parameters_with_gui:
                    with imgui_ctx.push_obj_id(param):
                        fl_widgets.text_custom(param.name + ":")
                        changed = param.parameter_with_gui.call_gui_edit() or changed
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
        if self.output_data_with_gui is None:
            return
        if self.input_data_with_gui is None:
            input_data = None
        else:
            input_data = self.input_data_with_gui.get()

        if self.function is not None:
            if input_data is None and not isinstance(self.function, SourceWithGui):
                r = None
            else:
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
