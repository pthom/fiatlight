from __future__ import annotations
from fiatlight.core import FunctionNode, FunctionNodeLink, UnspecifiedValue, BoolFunction, AnyDataWithGui
from fiatlight.core import Error, Unspecified
from fiatlight.core.function_with_gui import ParamWithGui
from fiatlight import widgets, JsonDict
from imgui_bundle import imgui, imgui_node_editor as ed, ImVec2, imgui_ctx, hello_imgui, imgui_node_editor_ctx as ed_ctx
from fiatlight.widgets.fontawesome6_ctx import icons_fontawesome_6, fontawesome_6_ctx
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class InputParamHeaderLineElements:
    """Data to be presented in a header line"""

    input_pin_color: widgets.ColorType = widgets.ColorType.InputPin

    status_icon: str | None = None
    status_icon_tooltips: List[str] | None = None

    param_name: str | None = None
    param_name_tooltip: str | None = None

    value_as_str: str | None = None

    show_details_button: bool = False
    details_button_tooltip: str = ""


class OutputHeaderLineElements:
    """Data to be presented in a header line"""

    output_pin_color: widgets.ColorType = widgets.ColorType.OutputPin

    status_icon: str | None = None
    status_icon_tooltips: List[str] | None = None

    value_as_str: str | None = None

    show_details_button: bool = False
    details_button_tooltip: str = ""


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


def _my_collapsible_button(expanded: bool, tooltip_part: str) -> bool:
    """A button that toggles between expanded and collapsed states.
    Returns true if expanded, false if collapsed.
    Displays as a caret pointing down if expanded, and right if collapsed, as imgui.collapsing_header() does.
    """
    icon = icons_fontawesome_6.ICON_FA_CARET_DOWN if expanded else icons_fontawesome_6.ICON_FA_CARET_RIGHT
    tooltip = "Hide " + tooltip_part if expanded else "Show " + tooltip_part
    with fontawesome_6_ctx():
        clicked = imgui.button(icon)
        if imgui.is_item_hovered():
            widgets.osd_widgets.set_tooltip(tooltip)
        if not clicked:
            return expanded
        else:
            return not expanded


class FunctionNodeGui:
    """The GUI representation as a visual node for a FunctionNode"""

    function_node: FunctionNode

    node_id: ed.NodeId
    pins_input: Dict[str, ed.PinId]
    pins_output: Dict[int, ed.PinId]

    node_size: ImVec2 | None = None  # will be set after the node is drawn once

    _MIN_NODE_WIDTH_EM = 9

    # user settings
    show_input_details: Dict[str, bool] = {}
    show_output_details: Dict[int, bool] = {}

    def __init__(self, function_node: FunctionNode) -> None:
        self.function_node = function_node

        self.node_id = ed.NodeId.create()

        self.pins_input = {}
        for input_with_gui in self.function_node.function_with_gui.inputs_with_gui:
            self.pins_input[input_with_gui.name] = ed.PinId.create()

        self.pins_output = {}
        for i, output_with_gui in enumerate(self.function_node.function_with_gui.outputs_with_gui):
            self.pins_output[i] = ed.PinId.create()

        self.show_input_details = {
            input_with_gui.name: False for input_with_gui in self.function_node.function_with_gui.inputs_with_gui
        }
        self.show_output_details = {i: True for i in range(len(self.function_node.function_with_gui.outputs_with_gui))}

    def _call_gui_present(self, value_with_gui: AnyDataWithGui[Any]) -> None:
        value = value_with_gui.value
        fn_present = value_with_gui.callbacks.present_custom
        assert value_with_gui.can_present_value()
        assert not isinstance(value, (Error, Unspecified))
        assert fn_present is not None
        fn_present()

    def _call_gui_edit(self, input_param: ParamWithGui[Any]) -> bool:
        value = input_param.data_with_gui.value
        default_param_value = input_param.default_value
        data_callbacks = input_param.data_with_gui.callbacks

        @dataclass
        class EditElements:
            fn_set_unset: BoolFunction | None = None
            fn_edit: BoolFunction | None = None

        edit_elements = EditElements()

        #
        # Set / unset button: fill edit_elements.fn_set_unset
        #
        if isinstance(value, (Error, Unspecified)):
            # For Error or Unspecified values
            value_to_create: Unspecified | Any = UnspecifiedValue
            value_to_create_tooltip = ""
            if not isinstance(default_param_value, Unspecified):
                value_to_create = default_param_value
                value_to_create_tooltip = "Create using default param value."
            else:
                if data_callbacks.default_value_provider is not None:
                    value_to_create = data_callbacks.default_value_provider()
                    value_to_create_tooltip = "Create using default value provider for this type."

            if not isinstance(value_to_create, Unspecified):
                # For Error or Unspecified values, when a default value is available
                def fn_set_unset() -> bool:
                    with fontawesome_6_ctx():
                        set_changed = False
                        if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_PLUS):
                            input_param.data_with_gui.value = value_to_create
                            set_changed = True
                        if imgui.is_item_hovered():
                            widgets.osd_widgets.set_tooltip(value_to_create_tooltip)
                    return set_changed

                edit_elements.fn_set_unset = fn_set_unset

            else:
                # For Error or Unspecified values, when no default value is available
                def fn_set_unset() -> bool:
                    with fontawesome_6_ctx():
                        imgui.button(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION)
                        if imgui.is_item_hovered():
                            widgets.osd_widgets.set_tooltip("No default value provider!")
                        return False

                edit_elements.fn_set_unset = fn_set_unset

        else:
            # For specified values
            def fn_set_unset() -> bool:
                with fontawesome_6_ctx():
                    set_changed = False
                    if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_MINUS):
                        input_param.data_with_gui.value = UnspecifiedValue
                        set_changed = True
                    if imgui.is_item_hovered():
                        widgets.osd_widgets.set_tooltip("Unset this parameter.")
                    return set_changed

            edit_elements.fn_set_unset = fn_set_unset

        #
        # fill edit_elements.fn_edit
        #
        if isinstance(value, (Error, Unspecified)):

            def fn_edit() -> bool:
                imgui.text(str(value))
                return False

            edit_elements.fn_edit = fn_edit
        else:

            def fn_edit() -> bool:
                changed = False
                if data_callbacks.edit is not None:
                    changed = changed or data_callbacks.edit()
                else:
                    imgui.text("No editor")
                return changed

            edit_elements.fn_edit = fn_edit

        #
        # Call the functions
        #
        changed = False
        imgui.begin_horizontal("edit")
        if edit_elements.fn_edit is not None:
            imgui.begin_vertical("edit")
            changed = changed or edit_elements.fn_edit()
            imgui.end_vertical()
        imgui.spring()
        if edit_elements.fn_set_unset is not None:
            changed = changed or edit_elements.fn_set_unset()
        imgui.end_horizontal()
        return changed

    def _output_header_elements(self, output_idx: int) -> OutputHeaderLineElements:
        """Return the elements to be presented in a header line"""
        assert 0 <= output_idx < len(self.function_node.function_with_gui.outputs_with_gui)

        output_with_gui = self.function_node.function_with_gui.outputs_with_gui[output_idx]
        r = OutputHeaderLineElements()

        # fill r.value_as_str and color
        value = output_with_gui.data_with_gui.value
        if isinstance(value, Unspecified):
            r.value_as_str = "Unspecified!"
            r.output_pin_color = widgets.ColorType.OutputPinUnspecified
        elif isinstance(value, Error):
            r.value_as_str = "Error!"
            r.output_pin_color = widgets.ColorType.OutputPinWithError
        else:
            r.value_as_str = output_with_gui.data_with_gui.datatype_value_to_str(value)
            r.output_pin_color = widgets.ColorType.OutputPin

        # fill r.status_icon and r.status_icon_tooltips
        has_output_links = len(self.function_node.output_links_for_idx(output_idx)) > 0
        if has_output_links:
            r.status_icon = icons_fontawesome_6.ICON_FA_LINK
            r.status_icon_tooltips = self.function_node.output_node_links_info(output_idx)
        else:
            r.status_icon = icons_fontawesome_6.ICON_FA_PLUG_CIRCLE_XMARK
            r.status_icon_tooltips = ["Unlinked output!"]

        # fill r.show_details_button and r.details_button_tooltip
        can_present = output_with_gui.data_with_gui.can_present_value()
        if can_present:
            r.show_details_button = True
            r.details_button_tooltip = "output details"

        return r

    def _input_param_header_elements(self, input_param: ParamWithGui[Any]) -> InputParamHeaderLineElements:
        """Return the elements to be presented in a header line"""
        r = InputParamHeaderLineElements()
        has_link = self.function_node.has_input_link(input_param.name)
        r.status_icon_tooltips = []

        # fill status_icon and status_icon_tooltips if there is a link
        if has_link:
            r.status_icon = icons_fontawesome_6.ICON_FA_LINK
            node_link_info = self.function_node.input_node_link_info(input_param.name)
            if node_link_info is not None:
                r.status_icon_tooltips.append(node_link_info)

        # fill status_icon and status_icon_tooltips if user edited
        if not has_link and not isinstance(input_param.data_with_gui.value, (Unspecified, Error)):
            r.status_icon = icons_fontawesome_6.ICON_FA_PENCIL
            r.status_icon_tooltips.append("User edited")

        # fill value_as_str and input_pin_color (may set status_icon and status_icon_tooltips on error/unspecified)
        if isinstance(input_param.data_with_gui.value, Error):
            r.input_pin_color = widgets.ColorType.InputPinWithError
            r.status_icon = icons_fontawesome_6.ICON_FA_BOMB
            r.status_icon_tooltips.append("Error!")
            r.value_as_str = "Error!"
        elif isinstance(input_param.data_with_gui.value, Unspecified):
            if isinstance(input_param.default_value, Unspecified):
                r.input_pin_color = widgets.ColorType.InputPinUnspecified
                r.status_icon = icons_fontawesome_6.ICON_FA_CIRCLE_EXCLAMATION
                r.status_icon_tooltips.append("Unspecified!")
                r.value_as_str = "Unspecified!"
            else:
                r.status_icon = icons_fontawesome_6.ICON_FA_PLUG_CIRCLE_XMARK
                r.status_icon_tooltips.append("Unspecified! Using default value.")
                r.value_as_str = input_param.data_with_gui.datatype_value_to_str(input_param.default_value)
        else:
            r.value_as_str = input_param.data_with_gui.datatype_value_to_str(input_param.data_with_gui.value)

        # fill param_name and param_name_tooltip
        r.param_name = input_param.name
        r.param_name_tooltip = "This is an example param doc"

        # fill show_details_button and details_button_tooltip
        has_link = self.function_node.has_input_link(input_param.name)
        if has_link:
            can_present = input_param.data_with_gui.can_present_value()
            if can_present:
                r.show_details_button = True
                r.details_button_tooltip = "linked input details"
        else:
            r.show_details_button = True
            r.details_button_tooltip = "edit input"

        return r

    def _draw_output_header_line(self, idx_output: int) -> None:
        header_elements = self._output_header_elements(idx_output)

        # If multiple outputs, show "Output X:"
        if len(self.function_node.function_with_gui.outputs_with_gui) > 1:
            imgui.text(f"Output {idx_output}:")

        # Show one line value
        if header_elements.value_as_str is not None:
            widgets.text_maybe_truncated(header_elements.value_as_str, max_width_chars=40, max_lines=1)

        # Align to the right
        imgui.spring()

        # Show present button, if a custom present callback is available
        if header_elements.show_details_button:
            self.show_output_details[idx_output] = _my_collapsible_button(
                self.show_output_details[idx_output], header_elements.details_button_tooltip
            )

        # Show colored pin with possible tooltip
        with imgui_ctx.push_style_color(imgui.Col_.text.value, widgets.COLORS[header_elements.output_pin_color]):
            with ed_ctx.begin_pin(self.pins_output[idx_output], ed.PinKind.output):
                ed.pin_pivot_alignment(ImVec2(1, 0.5))
                with fontawesome_6_ctx():
                    if header_elements.status_icon is not None:
                        imgui.text(header_elements.status_icon)
                        if header_elements.status_icon_tooltips is not None:
                            tooltip_str = "\n".join(header_elements.status_icon_tooltips)
                            if tooltip_str != "" and imgui.is_item_hovered():
                                widgets.osd_widgets.set_tooltip(tooltip_str)

    def _draw_input_header_line(self, input_param: ParamWithGui[Any]) -> None:
        imgui.begin_horizontal("input")
        header_elements = self._input_param_header_elements(input_param)
        with imgui_ctx.push_style_color(imgui.Col_.text.value, widgets.COLORS[header_elements.input_pin_color]):
            input_name = input_param.name
            with ed_ctx.begin_pin(self.pins_input[input_name], ed.PinKind.input):
                ed.pin_pivot_alignment(ImVec2(0, 0.5))
                with fontawesome_6_ctx():
                    # Pin status icon
                    if header_elements.status_icon is not None:
                        imgui.text(header_elements.status_icon)
                        if header_elements.status_icon_tooltips is not None:
                            tooltip_str = "\n".join(header_elements.status_icon_tooltips)
                            if tooltip_str != "" and imgui.is_item_hovered():
                                widgets.osd_widgets.set_tooltip(tooltip_str)

                    # Param name
                    if header_elements.param_name is not None:
                        imgui.text(header_elements.param_name)
                        if header_elements.param_name_tooltip is not None and imgui.is_item_hovered():
                            widgets.osd_widgets.set_tooltip(header_elements.param_name_tooltip)

        if header_elements.value_as_str is not None:
            widgets.text_maybe_truncated(header_elements.value_as_str, max_width_chars=40, max_lines=1)

        if header_elements.show_details_button:
            imgui.spring()
            self.show_input_details[input_name] = _my_collapsible_button(
                self.show_input_details[input_name], header_elements.details_button_tooltip
            )

        imgui.end_horizontal()

    def _draw_exception_message(self) -> None:
        from fiatlight.app_runner import FIATLIGHT_GUI_CONFIG

        last_exception_message = self.function_node.function_with_gui.last_exception_message
        if last_exception_message is None:
            return

        min_exception_width = hello_imgui.em_size(16)
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

    def _draw_title(self, unique_name: str) -> None:
        fn_name = self.function_node.function_with_gui.name
        widgets.text_maybe_truncated(fn_name)
        if unique_name != fn_name:
            if imgui.is_item_hovered():
                widgets.osd_widgets.set_tooltip(f" (id: {unique_name})")

        fn_doc = self.function_node.function_with_gui.doc()
        if fn_doc is not None:
            imgui.spring()
            with fontawesome_6_ctx():
                imgui.text(icons_fontawesome_6.ICON_FA_CIRCLE_QUESTION)
            if imgui.is_item_hovered():
                widgets.osd_widgets.set_tooltip(fn_doc)

    def _draw_invoke_options(self) -> None:
        invoke_changed, self.function_node.function_with_gui.invoke_automatically = imgui.checkbox(
            "Auto refresh", self.function_node.function_with_gui.invoke_automatically
        )
        if invoke_changed and self.function_node.function_with_gui.invoke_automatically:
            self.function_node.invoke_function()

        if self.function_node.function_with_gui.dirty:
            imgui.begin_horizontal("refresh")
            if imgui.button("Refresh"):
                self.function_node.invoke_function()
            imgui.text("(refresh needed)")
            imgui.end_horizontal()

    def _draw_function_outputs(self) -> None:
        for idx_output, output_param in enumerate(self.function_node.function_with_gui.outputs_with_gui):
            with imgui_ctx.push_obj_id(output_param):
                with imgui_ctx.begin_group():
                    with imgui_ctx.begin_horizontal("outputH"):
                        self._draw_output_header_line(idx_output)
                    can_present = output_param.data_with_gui.can_present_value()
                    if can_present and self.show_output_details[idx_output]:
                        self._call_gui_present(output_param.data_with_gui)

    def _draw_function_inputs(self) -> bool:
        changed = False

        if len(self.function_node.function_with_gui.inputs_with_gui) > 0:
            widgets.node_utils.node_separator(self.node_id, text="Params")

        for input_param in self.function_node.function_with_gui.inputs_with_gui:
            with imgui_ctx.push_obj_id(input_param):
                input_name = input_param.name

                self._draw_input_header_line(input_param)

                if self.show_input_details[input_name]:
                    shall_show_edit = not self.function_node.has_input_link(input_name)
                    if shall_show_edit:
                        changed = changed or self._call_gui_edit(input_param)
                    else:
                        self._call_gui_present(input_param.data_with_gui)

        return changed

    def draw_node(self, unique_name: str) -> None:
        with ed_ctx.begin_node(self.node_id):
            with imgui_ctx.begin_vertical("node_content"):
                # Title and doc
                with imgui_ctx.begin_horizontal("Title"):
                    self._draw_title(unique_name)
                imgui.dummy(ImVec2(hello_imgui.em_size(self._MIN_NODE_WIDTH_EM), 1))

                # Inputs
                inputs_changed = self._draw_function_inputs()
                if inputs_changed:
                    self.function_node.function_with_gui.dirty = True
                    if self.function_node.function_with_gui.invoke_automatically:
                        self.function_node.invoke_function()

                # Outputs
                output_separator_str = (
                    "Outputs" if len(self.function_node.function_with_gui.outputs_with_gui) > 1 else "Output"
                )
                widgets.node_utils.node_separator(self.node_id, text=output_separator_str)
                self._draw_invoke_options()
                # Exceptions, if any
                self._draw_exception_message()
                self._draw_function_outputs()
        self.node_size = ed.get_node_size(self.node_id)

    def save_gui_options_to_json(self) -> JsonDict:
        r = {
            "show_input_details": self.show_input_details,
            "show_output_details": self.show_output_details,
        }
        return r

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        show_input_details_as_dict_str_bool = json_data.get("show_input_details")
        if show_input_details_as_dict_str_bool is not None:
            for k, v in show_input_details_as_dict_str_bool.items():
                self.show_input_details[k] = v

        show_output_details_as_dict_str_bool = json_data.get("show_output_details")
        if show_output_details_as_dict_str_bool is not None:
            for k, v in show_output_details_as_dict_str_bool.items():
                self.show_output_details[int(k)] = v


def sandbox() -> None:
    from fiatlight.core import any_function_to_function_with_gui
    from imgui_bundle import immapp
    from enum import Enum

    class MyEnum(Enum):
        ONE = 1
        TWO = 2
        THREE = 3

    def add(
        # a: int | None = None,
        # e: MyEnum,
        # x: int = 1,
        # y: int = 2,
        # s: str = "Hello",
    ) -> List[str]:
        return ["Hello", "World", "!"]
        # return x + y + len(s) + e.value

    function_with_gui = any_function_to_function_with_gui(add, globals_dict=globals(), locals_dict=locals())
    function_node = FunctionNode(function_with_gui, name="add")
    function_node_gui = FunctionNodeGui(function_node)

    def gui() -> None:
        from fiatlight import widgets

        with ed_ctx.begin("Functions Graph"):
            function_node_gui.draw_node("add")
        widgets.osd_widgets.render()

    immapp.run(gui, with_node_editor=True, window_title="function_node_gui_sandbox")


if __name__ == "__main__":
    sandbox()
