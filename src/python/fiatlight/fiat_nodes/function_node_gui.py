from __future__ import annotations
from fiatlight.fiat_types import Error, Unspecified, UnspecifiedValue, BoolFunction, JsonDict
from fiatlight.fiat_core import FunctionNode, FunctionNodeLink, AnyDataWithGui
from fiatlight.fiat_config import FiatColorType, get_fiat_config
from fiatlight.fiat_core.function_with_gui import ParamWithGui
from imgui_bundle import imgui, imgui_node_editor as ed, ImVec2, imgui_ctx, hello_imgui, imgui_node_editor_ctx as ed_ctx
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx, osd_widgets
from fiatlight import fiat_widgets
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class InputParamHeaderLineElements:
    """Data to be presented in a header line"""

    input_pin_color: FiatColorType = FiatColorType.InputPin

    status_icon: str | None = None
    status_icon_tooltips: List[str] | None = None

    param_name: str | None = None
    param_name_tooltip: str | None = None

    value_as_str: str | None = None

    show_details_button: bool = False
    details_button_tooltip: str = ""


class OutputHeaderLineElements:
    """Data to be presented in a header line"""

    output_pin_color: FiatColorType = FiatColorType.OutputPin

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
            osd_widgets.set_tooltip(tooltip)
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

    # user settings
    show_input_details: Dict[str, bool] = {}
    show_output_details: Dict[int, bool] = {}
    inputs_expanded: bool = True
    outputs_expanded: bool = True

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

    def _call_gui_present_custom(self, value_with_gui: AnyDataWithGui[Any]) -> None:
        value = value_with_gui.value
        fn_present = value_with_gui.callbacks.present_custom
        if not value_with_gui.can_present_custom():
            return
        assert not isinstance(value, (Error, Unspecified))
        assert fn_present is not None
        fn_present()

    @staticmethod
    def _input_param_set_unset_gui(input_param: ParamWithGui[Any]) -> BoolFunction:
        """Return a gui function that sets or unsets the value of an input parameter."""
        value = input_param.data_with_gui.value
        default_param_value = input_param.default_value
        data_callbacks = input_param.data_with_gui.callbacks

        if not isinstance(value, (Error, Unspecified)):
            # For specified values
            def fn_set_unset_specified_value() -> bool:
                with fontawesome_6_ctx():
                    set_changed = False
                    if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_MINUS):
                        input_param.data_with_gui.value = UnspecifiedValue
                        set_changed = True
                    if imgui.is_item_hovered():
                        osd_widgets.set_tooltip("Unset this parameter.")
                    return set_changed

            return fn_set_unset_specified_value
        else:
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
                def fn_set_unset_with_default_value() -> bool:
                    with fontawesome_6_ctx():
                        set_changed = False
                        if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_PLUS):
                            input_param.data_with_gui.value = value_to_create
                            set_changed = True
                        if imgui.is_item_hovered():
                            osd_widgets.set_tooltip(value_to_create_tooltip)
                    return set_changed

                return fn_set_unset_with_default_value

            else:
                # For Error or Unspecified values, when no default value is available
                def fn_set_unset_with_no_provider() -> bool:
                    with fontawesome_6_ctx():
                        imgui.button(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION)
                        if imgui.is_item_hovered():
                            osd_widgets.set_tooltip("No default value provider!")
                        return False

                return fn_set_unset_with_no_provider

    @staticmethod
    def _input_param_edit_gui(input_param: ParamWithGui[Any]) -> BoolFunction:
        value = input_param.data_with_gui.value
        data_callbacks = input_param.data_with_gui.callbacks
        if isinstance(value, (Error, Unspecified)):

            def fn_display_error() -> bool:
                imgui.text(str(value))
                return False

            return fn_display_error
        else:

            def fn_edit() -> bool:
                changed = False
                if data_callbacks.edit is not None:
                    if data_callbacks.edit():
                        changed = True
                else:
                    imgui.text("No editor")
                return changed

            return fn_edit

    def _call_gui_edit(self, input_param: ParamWithGui[Any]) -> bool:
        fn_set_unset = self._input_param_set_unset_gui(input_param)
        fn_edit = self._input_param_edit_gui(input_param)

        changed = False
        with imgui_ctx.begin_horizontal("editH"):
            with imgui_ctx.begin_vertical("editV"):
                if fn_edit():
                    changed = True
            imgui.spring()
            if fn_set_unset():
                changed = True
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
            r.output_pin_color = FiatColorType.OutputPinUnspecified
        elif isinstance(value, Error):
            r.value_as_str = "Error!"
            r.output_pin_color = FiatColorType.OutputPinWithError
        else:
            r.value_as_str = output_with_gui.data_with_gui.datatype_value_to_str(value)
            r.output_pin_color = FiatColorType.OutputPin

        # fill r.status_icon and r.status_icon_tooltips
        has_output_links = len(self.function_node.output_links_for_idx(output_idx)) > 0
        if has_output_links:
            r.status_icon = icons_fontawesome_6.ICON_FA_LINK
            r.status_icon_tooltips = self.function_node.output_node_links_info(output_idx)
        else:
            r.status_icon = icons_fontawesome_6.ICON_FA_PLUG_CIRCLE_XMARK
            r.status_icon_tooltips = ["Unlinked output!"]

        # fill r.show_details_button and r.details_button_tooltip
        can_present = output_with_gui.data_with_gui.can_present_custom()
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
            r.input_pin_color = FiatColorType.InputPinWithError
            r.status_icon = icons_fontawesome_6.ICON_FA_BOMB
            r.status_icon_tooltips.append("Error!")
            r.value_as_str = "Error!"
        elif isinstance(input_param.data_with_gui.value, Unspecified):
            if isinstance(input_param.default_value, Unspecified):
                r.input_pin_color = FiatColorType.InputPinUnspecified
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
            can_present = input_param.data_with_gui.can_present_custom()
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
            fiat_widgets.text_maybe_truncated(header_elements.value_as_str, max_width_chars=40, max_lines=1)

        # Align to the right
        imgui.spring()

        # Show present button, if a custom present callback is available
        if header_elements.show_details_button:
            self.show_output_details[idx_output] = _my_collapsible_button(
                self.show_output_details[idx_output], header_elements.details_button_tooltip
            )

        # Show colored pin with possible tooltip
        with imgui_ctx.push_style_color(
            imgui.Col_.text.value,
            get_fiat_config().style.colors[header_elements.output_pin_color],
        ):
            with ed_ctx.begin_pin(self.pins_output[idx_output], ed.PinKind.output):
                ed.pin_pivot_alignment(ImVec2(1, 0.5))
                with fontawesome_6_ctx():
                    if header_elements.status_icon is not None:
                        imgui.text(header_elements.status_icon)
                        if header_elements.status_icon_tooltips is not None:
                            tooltip_str = "\n".join(header_elements.status_icon_tooltips)
                            if tooltip_str != "" and imgui.is_item_hovered():
                                osd_widgets.set_tooltip(tooltip_str)

    def _draw_input_header_line(self, input_param: ParamWithGui[Any]) -> None:
        imgui.begin_horizontal("input")
        header_elements = self._input_param_header_elements(input_param)
        with imgui_ctx.push_style_color(
            imgui.Col_.text.value, get_fiat_config().style.colors[header_elements.input_pin_color]
        ):
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
                                osd_widgets.set_tooltip(tooltip_str)

                    # Param name
                    if header_elements.param_name is not None:
                        imgui.text(header_elements.param_name)
                        if header_elements.param_name_tooltip is not None and imgui.is_item_hovered():
                            osd_widgets.set_tooltip(header_elements.param_name_tooltip)

        if header_elements.value_as_str is not None:
            fiat_widgets.text_maybe_truncated(header_elements.value_as_str, max_width_chars=40, max_lines=1)

        if header_elements.show_details_button:
            imgui.spring()
            self.show_input_details[input_name] = _my_collapsible_button(
                self.show_input_details[input_name], header_elements.details_button_tooltip
            )

        imgui.end_horizontal()

    def _draw_exception_message(self) -> None:
        from fiatlight.fiat_runner import FIATLIGHT_GUI_CONFIG

        last_exception_message = self.function_node.function_with_gui.last_exception_message
        if last_exception_message is None:
            return

        min_exception_width = hello_imgui.em_size(16)
        exception_width = min_exception_width
        if self.node_size is not None:
            exception_width = self.node_size.x - hello_imgui.em_size(2)
            if exception_width < min_exception_width:
                exception_width = min_exception_width
        fiat_widgets.text_maybe_truncated(
            "Exception:\n" + last_exception_message,
            max_width_pixels=exception_width,
            color=FIATLIGHT_GUI_CONFIG.colors.error,
        )

    def _draw_title(self, unique_name: str) -> None:
        fn_name = self.function_node.function_with_gui.name
        fiat_widgets.text_maybe_truncated(fn_name)
        if unique_name != fn_name:
            if imgui.is_item_hovered():
                osd_widgets.set_tooltip(f" (id: {unique_name})")

        if self.function_node.function_with_gui.has_doc():
            fn_doc = self.function_node.function_with_gui.get_function_doc()
            first_line = fn_doc.split("\n")[0]
            title_line = self.function_node.function_with_gui.name + "(): " + first_line
            remaining_text = fn_doc[len(first_line) :]

            def show_doc() -> None:
                from imgui_bundle import imgui_md

                imgui_md.render("## " + title_line)
                imgui.text_wrapped(remaining_text)

            with fontawesome_6_ctx():
                imgui.spring()
                popup_label = f"{unique_name}(): function documentation"
                btn_text = icons_fontawesome_6.ICON_FA_BOOK
                osd_widgets.show_void_popup_button(btn_text, popup_label, show_doc)

    def _draw_invoke_options(self) -> None:
        fn_with_gui = self.function_node.function_with_gui
        btn_size = hello_imgui.em_to_vec2(4, 0)

        with fontawesome_6_ctx():
            if fn_with_gui.invoke_automatically_can_set:
                invoke_changed, fn_with_gui.invoke_automatically = imgui.checkbox(
                    "##Auto refresh", self.function_node.function_with_gui.invoke_automatically
                )
                if imgui.is_item_hovered():
                    osd_widgets.set_tooltip("Tick to invoke automatically.")
                if invoke_changed and fn_with_gui.invoke_automatically:
                    self.function_node.invoke_function()

            if fn_with_gui.dirty:
                if imgui.button(icons_fontawesome_6.ICON_FA_ROTATE, btn_size):
                    self.function_node.invoke_function()
                if imgui.is_item_hovered():
                    osd_widgets.set_tooltip("Refresh needed! Click to refresh.")

            if not fn_with_gui.invoke_automatically:
                if not fn_with_gui.dirty:
                    imgui.text(icons_fontawesome_6.ICON_FA_CHECK)
                    if imgui.is_item_hovered():
                        osd_widgets.set_tooltip("Up to date!")
                else:
                    imgui.text(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION)
                    if imgui.is_item_hovered():
                        osd_widgets.set_tooltip("Refresh needed!")

    def _draw_function_outputs(self, unique_name: str) -> None:
        is_dirty = self.function_node.function_with_gui.dirty
        if is_dirty:
            imgui.push_style_color(imgui.Col_.text.value, get_fiat_config().style.colors[FiatColorType.TextDirtyOutput])
        for idx_output, output_param in enumerate(self.function_node.function_with_gui.outputs_with_gui):
            with imgui_ctx.push_obj_id(output_param):
                has_link = len(self.function_node.output_links_for_idx(idx_output)) > 0
                if not has_link and not self.outputs_expanded:
                    continue
                with imgui_ctx.begin_group():
                    with imgui_ctx.begin_horizontal("outputH"):
                        self._draw_output_header_line(idx_output)
                    can_present = output_param.data_with_gui.can_present_custom()
                    if can_present and self.show_output_details[idx_output]:
                        # capture the output_param for the lambda
                        # (otherwise, the lambda would capture the last output_param in the loop)
                        output_param_captured = output_param

                        def present_output() -> None:
                            # Present output can be called either directly in this window or in a detached window
                            self._call_gui_present_custom(output_param_captured.data_with_gui)

                        callbacks = output_param.data_with_gui.callbacks
                        can_present_custom_in_node = not callbacks.present_custom_popup_required
                        can_present_custom_in_popup = (
                            callbacks.present_custom_popup_required or callbacks.present_custom_popup_possible
                        )

                        if can_present_custom_in_popup:
                            popup_label = f"detached view - {unique_name}: output {idx_output}"
                            osd_widgets.show_void_popup_button("", popup_label, present_output)

                        if can_present_custom_in_node:
                            present_output()
        if is_dirty:
            imgui.pop_style_color()

    def _can_collapse_inputs(self) -> bool:
        # We can only collapse inputs that do not have a link
        # (since otherwise, the user would not be able to see the link status, and we have to display a pin anyway)
        if len(self.function_node.function_with_gui.inputs_with_gui) == 0:
            return False

        nb_inputs_with_links = 0
        for input_param in self.function_node.function_with_gui.inputs_with_gui:
            if self.function_node.has_input_link(input_param.name):
                nb_inputs_with_links += 1

        nb_inputs = len(self.function_node.function_with_gui.inputs_with_gui)
        return nb_inputs_with_links < nb_inputs

    def _can_collapse_outputs(self) -> bool:
        # We can only collapse outputs that do not have a link
        # (since otherwise, the user would not be able to see the link status, and we have to display a pin anyway)
        if len(self.function_node.function_with_gui.outputs_with_gui) <= 1:
            return False

        nb_outputs_with_links = 0
        for i, output_param in enumerate(self.function_node.function_with_gui.outputs_with_gui):
            if len(self.function_node.output_links_for_idx(i)) > 0:
                nb_outputs_with_links += 1

        nb_outputs = len(self.function_node.function_with_gui.outputs_with_gui)
        return nb_outputs_with_links < nb_outputs

    def _draw_function_inputs(self, unique_name: str) -> bool:
        changed = False

        if len(self.function_node.function_with_gui.inputs_with_gui) > 0:
            if self._can_collapse_inputs():
                changed, self.inputs_expanded = fiat_widgets.node_utils.node_collapsing_separator(
                    self.node_id, text="Params", expanded=self.inputs_expanded
                )
                if changed:
                    for k, v in self.show_input_details.items():
                        # We do not change the status of nodes that have a link
                        # (since they are hidden by default in the inputs, visible by default in the outputs)
                        has_link = self.function_node.has_input_link(k)
                        if not has_link:
                            self.show_input_details[k] = self.inputs_expanded
            else:
                self.inputs_expanded = True
                fiat_widgets.node_utils.node_separator(self.node_id, "Params")

        for input_param in self.function_node.function_with_gui.inputs_with_gui:
            with imgui_ctx.push_obj_id(input_param):
                input_name = input_param.name

                has_link = self.function_node.has_input_link(input_name)
                if not has_link and not self.inputs_expanded:
                    continue

                self._draw_input_header_line(input_param)

                if self.show_input_details[input_name]:
                    shall_show_edit = not self.function_node.has_input_link(input_name)
                    if shall_show_edit:
                        # capture the input_param for the lambda
                        # (otherwise, the lambda would capture the last input_param in the loop)
                        input_param_captured = input_param

                        def edit_input() -> bool:
                            # Edit input can be called either directly in this window or in a detached window
                            return self._call_gui_edit(input_param_captured)

                        callbacks = input_param.data_with_gui.callbacks
                        can_edit_in_node = not callbacks.edit_popup_required
                        can_edit_in_popup = callbacks.edit_popup_required or callbacks.edit_popup_possible
                        popup_label = f"detached view - {unique_name}(): edit input '{input_param.name}'"
                        btn_label = "" if can_edit_in_node else "edit"

                        if can_edit_in_popup:
                            osd_widgets.show_bool_popup_button(btn_label, popup_label, edit_input)

                        # Now that we can have a detached view, there are two ways
                        # that can change the input value:
                        if can_edit_in_node and edit_input():
                            # 1. The user edits the input value in this window
                            changed = True
                        if can_edit_in_popup and osd_widgets.get_popup_bool_return(btn_label):
                            # 2. The user edits the input value in a detached window
                            changed = True
                    else:
                        if input_param.data_with_gui.can_present_custom():
                            # capture the input_param for the lambda
                            # with a different name for the captured variable, because of
                            # python weird scoping rules
                            input_param_captured_2 = input_param

                            def present_input() -> None:
                                # Present input can be called either directly in this window or in a detached window
                                self._call_gui_present_custom(input_param_captured_2.data_with_gui)

                            callbacks = input_param.data_with_gui.callbacks
                            can_present_custom_in_node = not callbacks.present_custom_popup_required
                            can_present_custom_in_popup = (
                                callbacks.present_custom_popup_required or callbacks.present_custom_popup_possible
                            )

                            if can_present_custom_in_popup:
                                popup_label = f"detached view - {unique_name}() - input '{input_param.name}'"
                                osd_widgets.show_void_popup_button("", popup_label, present_input)

                            if can_present_custom_in_node:
                                present_input()
        return changed

    def draw_node(self, unique_name: str) -> None:
        with imgui_ctx.push_obj_id(self.function_node):
            with ed_ctx.begin_node(self.node_id):
                with imgui_ctx.begin_vertical("node_content"):
                    # Title and doc
                    with imgui_ctx.begin_horizontal("Title"):
                        self._draw_title(unique_name)
                    imgui.dummy(ImVec2(hello_imgui.em_size(get_fiat_config().style.node_minimum_width_em), 1))

                    # Inputs
                    inputs_changed = self._draw_function_inputs(unique_name)
                    if inputs_changed:
                        self.function_node.function_with_gui.dirty = True
                        if self.function_node.function_with_gui.invoke_automatically:
                            self.function_node.invoke_function()

                    #
                    # Outputs
                    #

                    # Outputs separator
                    output_separator_str = (
                        "Outputs" if len(self.function_node.function_with_gui.outputs_with_gui) > 1 else "Output"
                    )
                    if self._can_collapse_outputs():
                        changed, self.outputs_expanded = fiat_widgets.node_utils.node_collapsing_separator(
                            self.node_id, text=output_separator_str, expanded=self.outputs_expanded
                        )
                        if changed:
                            for i, v in self.show_output_details.items():
                                self.show_output_details[i] = self.outputs_expanded
                    else:
                        self.outputs_expanded = True
                        fiat_widgets.node_utils.node_separator(self.node_id, output_separator_str)

                    # Invoke options
                    with imgui_ctx.begin_horizontal("invoke_options"):
                        imgui.spring()
                        self._draw_invoke_options()

                    # Exceptions, if any
                    self._draw_exception_message()

                    # Outputs
                    self._draw_function_outputs(unique_name)
            self.node_size = ed.get_node_size(self.node_id)

    def save_gui_options_to_json(self) -> JsonDict:
        r = {
            "show_input_details": self.show_input_details,
            "show_output_details": self.show_output_details,
            "inputs_expanded": self.inputs_expanded,
            "outputs_expanded": self.outputs_expanded,
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

        self.inputs_expanded = json_data.get("inputs_expanded", True)
        self.outputs_expanded = json_data.get("outputs_expanded", True)


def sandbox() -> None:
    from fiatlight.fiat_core import to_function_with_gui
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

    function_with_gui = to_function_with_gui(add, globals_dict=globals(), locals_dict=locals())
    function_node = FunctionNode(function_with_gui, name="add")
    function_node_gui = FunctionNodeGui(function_node)

    def gui() -> None:
        with ed_ctx.begin("Functions Graph"):
            function_node_gui.draw_node("add")
        osd_widgets._OSD_WIDGETS.render()

    immapp.run(gui, with_node_editor=True, window_title="function_node_gui_sandbox")


if __name__ == "__main__":
    sandbox()
