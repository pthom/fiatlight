from __future__ import annotations
from fiatlight.fiat_types import Error, Unspecified, UnspecifiedValue, BoolFunction, JsonDict
from fiatlight.fiat_core import FunctionNode, FunctionNodeLink, AnyDataWithGui
from fiatlight.fiat_config import FiatColorType, get_fiat_config
from fiatlight.fiat_core.function_with_gui import ParamWithGui
from imgui_bundle import imgui, imgui_node_editor as ed, ImVec2, imgui_ctx, hello_imgui, imgui_node_editor_ctx as ed_ctx
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx, fiat_osd
from fiatlight import fiat_widgets
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class _InputParamHeaderLineElements:
    """Data to be presented in a header line"""

    input_pin_color: FiatColorType = FiatColorType.InputPin

    status_icon: str | None = None
    status_icon_tooltips: List[str] | None = None

    param_name: str | None = None

    value_as_str: str | None = None

    show_details_button: bool = False
    details_button_tooltip: str = ""


class _OutputHeaderLineElements:
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
            if f._function_node.function_with_gui == function_node_link.src_function_node.function_with_gui:
                self.start_id = f._pins_output[function_node_link.src_output_idx]
            if f._function_node.function_with_gui == function_node_link.dst_function_node.function_with_gui:
                self.end_id = f._pins_input[function_node_link.dst_input_name]
        assert hasattr(self, "start_id")
        assert hasattr(self, "end_id")

    def draw(self) -> None:
        ed.link(self.link_id, self.start_id, self.end_id)


@dataclass
class _FunctionDoc:
    title: str | None = None
    doc: str | None = None
    source_code: str | None = None

    def has_info(self) -> bool:
        return self.title is not None or self.doc is not None or self.source_code is not None


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
            fiat_osd.set_tooltip(tooltip)
        if not clicked:
            return expanded
        else:
            return not expanded


class FunctionNodeGui:
    """The GUI representation as a visual node for a FunctionNode"""

    # ------------------------------------------------------------------------------------------------------------------
    # Members
    # All are private
    # ------------------------------------------------------------------------------------------------------------------

    # A reference to the FunctionNode
    # (which references the FunctionWithGui, which references the function)
    _function_node: FunctionNode

    # The node Ids for imgui_node_editor
    _node_id: ed.NodeId
    _pins_input: Dict[str, ed.PinId]
    _pins_output: Dict[int, ed.PinId]

    # The current size of the node
    # (it varies depending on the content)
    _node_size: ImVec2 | None = None  # will be set after the node is drawn once

    _function_doc: _FunctionDoc

    # internals of the function
    _fiat_internals_with_gui: Dict[str, AnyDataWithGui[Any]]

    # user settings:
    # Shall we show the details of the inputs/outputs?
    # Those settings are saved in the user settings file
    _show_input_details: Dict[str, bool] = {}
    _inputs_expanded: bool = True
    _show_output_details: Dict[int, bool] = {}
    _outputs_expanded: bool = True
    _show_internals_details: Dict[str, bool] = {}
    _internals_expanded: bool = True

    # ------------------------------------------------------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, function_node: FunctionNode) -> None:
        self._function_node = function_node

        self._node_id = ed.NodeId.create()

        self._pins_input = {}
        for input_with_gui in self._function_node.function_with_gui.inputs_with_gui:
            self._pins_input[input_with_gui.name] = ed.PinId.create()

        self._pins_output = {}
        for i, output_with_gui in enumerate(self._function_node.function_with_gui.outputs_with_gui):
            self._pins_output[i] = ed.PinId.create()

        self._show_input_details = {
            input_with_gui.name: False for input_with_gui in self._function_node.function_with_gui.inputs_with_gui
        }
        self._show_output_details = {
            i: True for i in range(len(self._function_node.function_with_gui.outputs_with_gui))
        }

        self._fill_function_doc()
        self._fiat_internals_with_gui = {}

    # ------------------------------------------------------------------------------------------------------------------
    # Doc
    # ------------------------------------------------------------------------------------------------------------------
    def _fill_function_doc(self) -> None:
        self._function_doc = _FunctionDoc()
        fn_doc = self._function_node.function_with_gui.get_function_doc()
        if fn_doc is not None:
            first_line = fn_doc.split("\n")[0]
            title_line = self._function_node.function_with_gui.name + "(): " + first_line
            remaining_text = fn_doc[len(first_line) :]
            self._function_doc.title = title_line
            self._function_doc.doc = remaining_text

        self._function_doc.source_code = self._function_node.function_with_gui.get_function_source_code()

    def _has_doc(self) -> bool:
        return self._function_doc.has_info()

    # ------------------------------------------------------------------------------------------------------------------
    # Draw the node
    # This is the heart of the fiatlight, with `draw_node` being the main function
    # ------------------------------------------------------------------------------------------------------------------
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
                        fiat_osd.set_tooltip("Unset this parameter.")
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
                            fiat_osd.set_tooltip(value_to_create_tooltip)
                    return set_changed

                return fn_set_unset_with_default_value

            else:
                # For Error or Unspecified values, when no default value is available
                def fn_set_unset_with_no_provider() -> bool:
                    with fontawesome_6_ctx():
                        imgui.button(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION)
                        if imgui.is_item_hovered():
                            fiat_osd.set_tooltip("No default value provider!")
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

    def _output_header_elements(self, output_idx: int) -> _OutputHeaderLineElements:
        """Return the elements to be presented in a header line"""
        assert 0 <= output_idx < len(self._function_node.function_with_gui.outputs_with_gui)

        output_with_gui = self._function_node.function_with_gui.outputs_with_gui[output_idx]
        r = _OutputHeaderLineElements()

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
        has_output_links = len(self._function_node.output_links_for_idx(output_idx)) > 0
        if has_output_links:
            r.status_icon = icons_fontawesome_6.ICON_FA_LINK
            r.status_icon_tooltips = self._function_node.output_node_links_info(output_idx)
        else:
            r.status_icon = icons_fontawesome_6.ICON_FA_PLUG_CIRCLE_XMARK
            r.status_icon_tooltips = ["Unlinked output!"]

        # fill r.show_details_button and r.details_button_tooltip
        can_present = output_with_gui.data_with_gui.can_present_custom()
        if can_present:
            r.show_details_button = True
            r.details_button_tooltip = "output details"

        return r

    def _input_param_header_elements(self, input_param: ParamWithGui[Any]) -> _InputParamHeaderLineElements:
        """Return the elements to be presented in a header line"""
        r = _InputParamHeaderLineElements()
        has_link = self._function_node.has_input_link(input_param.name)
        r.status_icon_tooltips = []

        # fill status_icon and status_icon_tooltips if there is a link
        if has_link:
            r.status_icon = icons_fontawesome_6.ICON_FA_LINK
            node_link_info = self._function_node.input_node_link_info(input_param.name)
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

        # fill show_details_button and details_button_tooltip
        has_link = self._function_node.has_input_link(input_param.name)
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
        if len(self._function_node.function_with_gui.outputs_with_gui) > 1:
            imgui.text(f"Output {idx_output}:")

        # Show one line value
        if header_elements.value_as_str is not None:
            fiat_widgets.text_maybe_truncated(header_elements.value_as_str, max_width_chars=40, max_lines=1)

        # Align to the right
        imgui.spring()

        # Show present button, if a custom present callback is available
        if header_elements.show_details_button:
            self._show_output_details[idx_output] = _my_collapsible_button(
                self._show_output_details[idx_output], header_elements.details_button_tooltip
            )

        # Show colored pin with possible tooltip
        with imgui_ctx.push_style_color(
            imgui.Col_.text.value,
            get_fiat_config().style.colors[header_elements.output_pin_color],
        ):
            with ed_ctx.begin_pin(self._pins_output[idx_output], ed.PinKind.output):
                ed.pin_pivot_alignment(ImVec2(1, 0.5))
                with fontawesome_6_ctx():
                    if header_elements.status_icon is not None:
                        imgui.text(header_elements.status_icon)
                        if header_elements.status_icon_tooltips is not None:
                            tooltip_str = "\n".join(header_elements.status_icon_tooltips)
                            if tooltip_str != "" and imgui.is_item_hovered():
                                fiat_osd.set_tooltip(tooltip_str)

    def _draw_input_header_line(self, input_param: ParamWithGui[Any]) -> None:
        imgui.begin_horizontal("input")
        header_elements = self._input_param_header_elements(input_param)
        with imgui_ctx.push_style_color(
            imgui.Col_.text.value, get_fiat_config().style.colors[header_elements.input_pin_color]
        ):
            input_name = input_param.name
            with ed_ctx.begin_pin(self._pins_input[input_name], ed.PinKind.input):
                ed.pin_pivot_alignment(ImVec2(0, 0.5))
                with fontawesome_6_ctx():
                    # Pin status icon
                    if header_elements.status_icon is not None:
                        imgui.text(header_elements.status_icon)
                        if header_elements.status_icon_tooltips is not None:
                            tooltip_str = "\n".join(header_elements.status_icon_tooltips)
                            if tooltip_str != "" and imgui.is_item_hovered():
                                fiat_osd.set_tooltip(tooltip_str)

                    # Param name
                    if header_elements.param_name is not None:
                        imgui.text(header_elements.param_name)

        if header_elements.value_as_str is not None:
            fiat_widgets.text_maybe_truncated(header_elements.value_as_str, max_width_chars=40, max_lines=1)

        if header_elements.show_details_button:
            imgui.spring()
            self._show_input_details[input_name] = _my_collapsible_button(
                self._show_input_details[input_name], header_elements.details_button_tooltip
            )

        imgui.end_horizontal()

    def _draw_exception_message(self) -> None:
        from fiatlight.fiat_runner import FIATLIGHT_GUI_CONFIG

        last_exception_message = self._function_node.function_with_gui.last_exception_message
        if last_exception_message is None:
            return

        min_exception_width = hello_imgui.em_size(16)
        exception_width = min_exception_width
        if self._node_size is not None:
            exception_width = self._node_size.x - hello_imgui.em_size(2)
            if exception_width < min_exception_width:
                exception_width = min_exception_width
        fiat_widgets.text_maybe_truncated(
            "Exception:\n" + last_exception_message,
            max_width_pixels=exception_width,
            color=FIATLIGHT_GUI_CONFIG.colors.error,
        )

        # Raise the exception so that the user can debug it
        with fontawesome_6_ctx():
            # if imgui.button(icons_fontawesome_6.ICON_FA_BOMB):
            #     imgui.open_popup("Confirm Raise exception")
            # if imgui.is_item_hovered():
            #     fiat_osd.set_tooltip("Raise this exception to debug it.")

            btn_label = icons_fontawesome_6.ICON_FA_BOMB + " Debug this exception"
            popup_label = "Confirm Raise exception"

            def confirmation_gui() -> None:
                msg = """
                Are you sure you want to raise this exception?

                The function will be re-invoked,
                and the exception will be raised again.

                This application will crash (!!!),
                and you will be able to debug
                the exception in your debugger.
                """
                # align the text to the left
                lines = msg.split("\n")
                lines = list(map(str.strip, lines))
                msg = "\n".join(lines)

                imgui.text(msg)
                if imgui.button("Yes, raise the exception"):
                    get_fiat_config().exception_config.catch_function_exceptions = False
                    self._function_node.function_with_gui.dirty = True
                    self._function_node.function_with_gui.invoke()
                    imgui.close_current_popup()  # close the popup (which will never happen, we will crash)
                imgui.same_line()

            fiat_osd.show_void_popup_button(btn_label, popup_label, confirmation_gui)

    def _render_function_doc(self, unique_name: str) -> None:
        if not self._has_doc():
            return

        def show_doc() -> None:
            from imgui_bundle import imgui_md

            if self._function_doc.title is not None:
                imgui_md.render("## " + self._function_doc.title)
            if self._function_doc.doc is not None:
                imgui.text_wrapped(self._function_doc.doc)
            if self._function_doc.source_code is not None:
                md = "### Source code\n\n"
                md += f"```python\n{self._function_doc.source_code}\n```"
                imgui_md.render(md)

        with fontawesome_6_ctx():
            imgui.spring()
            popup_label = f"{unique_name}(): function documentation"
            btn_text = icons_fontawesome_6.ICON_FA_BOOK
            fiat_osd.show_void_popup_button(btn_text, popup_label, show_doc)

    def _draw_title(self, unique_name: str) -> None:
        fn_name = self._function_node.function_with_gui.name
        imgui.text(fn_name)
        if unique_name != fn_name:
            imgui.text(f" (id: {unique_name})")

        self._render_function_doc(unique_name)

    def _draw_invoke_options(self) -> None:
        fn_with_gui = self._function_node.function_with_gui
        btn_size = hello_imgui.em_to_vec2(4, 0)

        with fontawesome_6_ctx():
            if fn_with_gui.invoke_automatically_can_set:
                invoke_changed, fn_with_gui.invoke_automatically = imgui.checkbox(
                    "##Auto refresh", self._function_node.function_with_gui.invoke_automatically
                )
                if imgui.is_item_hovered():
                    fiat_osd.set_tooltip("Tick to invoke automatically.")
                if invoke_changed and fn_with_gui.invoke_automatically:
                    self._function_node.invoke_function()

            if fn_with_gui.dirty:
                if imgui.button(icons_fontawesome_6.ICON_FA_ROTATE, btn_size):
                    self._function_node.invoke_function()
                if imgui.is_item_hovered():
                    fiat_osd.set_tooltip("Refresh needed! Click to refresh.")

            if not fn_with_gui.invoke_automatically:
                if not fn_with_gui.dirty:
                    imgui.text(icons_fontawesome_6.ICON_FA_CHECK)
                    if imgui.is_item_hovered():
                        fiat_osd.set_tooltip("Up to date!")
                else:
                    imgui.text(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION)
                    if imgui.is_item_hovered():
                        fiat_osd.set_tooltip("Refresh needed!")

    def _draw_one_output(self, idx_output: int, unique_name: str) -> None:
        output_param = self._function_node.function_with_gui.outputs_with_gui[idx_output]
        with imgui_ctx.push_obj_id(output_param):
            with imgui_ctx.begin_horizontal("outputH"):
                self._draw_output_header_line(idx_output)
            can_present = output_param.data_with_gui.can_present_custom()
            if can_present and self._show_output_details[idx_output]:
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
                    fiat_osd.show_void_popup_button("", popup_label, present_output)

                if can_present_custom_in_node:
                    present_output()

    def _draw_function_outputs(self, unique_name: str) -> None:
        is_dirty = self._function_node.function_with_gui.dirty
        if is_dirty:
            imgui.push_style_color(imgui.Col_.text.value, get_fiat_config().style.colors[FiatColorType.TextDirtyOutput])
        for idx_output, output_param in enumerate(self._function_node.function_with_gui.outputs_with_gui):
            has_link = len(self._function_node.output_links_for_idx(idx_output)) > 0
            if not has_link and not self._outputs_expanded:
                continue
            with imgui_ctx.begin_group():
                self._draw_one_output(idx_output, unique_name)
        if is_dirty:
            imgui.pop_style_color()

    def _can_collapse_inputs(self) -> bool:
        # We can only collapse inputs that do not have a link
        # (since otherwise, the user would not be able to see the link status, and we have to display a pin anyway)
        if len(self._function_node.function_with_gui.inputs_with_gui) == 0:
            return False

        nb_inputs_with_links = 0
        for input_param in self._function_node.function_with_gui.inputs_with_gui:
            if self._function_node.has_input_link(input_param.name):
                nb_inputs_with_links += 1

        nb_inputs = len(self._function_node.function_with_gui.inputs_with_gui)
        return nb_inputs_with_links < nb_inputs

    def _can_collapse_outputs(self) -> bool:
        # We can only collapse outputs that do not have a link
        # (since otherwise, the user would not be able to see the link status, and we have to display a pin anyway)
        if len(self._function_node.function_with_gui.outputs_with_gui) <= 1:
            return False

        nb_outputs_with_links = 0
        for i, output_param in enumerate(self._function_node.function_with_gui.outputs_with_gui):
            if len(self._function_node.output_links_for_idx(i)) > 0:
                nb_outputs_with_links += 1

        nb_outputs = len(self._function_node.function_with_gui.outputs_with_gui)
        return nb_outputs_with_links < nb_outputs

    def _draw_one_input_edit(self, input_param: ParamWithGui[Any], unique_name: str) -> bool:
        changed = False
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
            fiat_osd.show_bool_popup_button(btn_label, popup_label, edit_input)

        # Now that we can have a detached view, there are two ways
        # that can change the input value:
        if can_edit_in_node and edit_input():
            # 1. The user edits the input value in this window
            changed = True
        if can_edit_in_popup and fiat_osd.get_popup_bool_return(btn_label):
            # 2. The user edits the input value in a detached window
            changed = True

        return changed

    def _draw_one_input_present_custom(self, input_param: ParamWithGui[Any], unique_name: str) -> None:
        # capture the input_param for the lambda
        # with a different name for the captured variable, because of
        # python weird scoping rules
        input_param_captured_2 = input_param

        def present_input() -> None:
            # Present input can be called either directly in this window or in a detached window
            self._call_gui_present_custom(input_param_captured_2.data_with_gui)

        callbacks = input_param.data_with_gui.callbacks
        can_present_custom_in_node = not callbacks.present_custom_popup_required
        can_present_custom_in_popup = callbacks.present_custom_popup_required or callbacks.present_custom_popup_possible

        if can_present_custom_in_popup:
            popup_label = f"detached view - {unique_name}() - input '{input_param.name}'"
            fiat_osd.show_void_popup_button("", popup_label, present_input)

        if can_present_custom_in_node:
            present_input()

    def _draw_one_input(self, input_param: ParamWithGui[Any], unique_name: str) -> bool:
        with imgui_ctx.push_obj_id(input_param):
            input_name = input_param.name

            has_link = self._function_node.has_input_link(input_name)
            if not has_link and not self._inputs_expanded:
                return False

            self._draw_input_header_line(input_param)

            if not self._show_input_details[input_name]:
                return False

            shall_show_edit = not self._function_node.has_input_link(input_name)
            if shall_show_edit:
                return self._draw_one_input_edit(input_param, unique_name)
            else:
                if input_param.data_with_gui.can_present_custom():
                    self._draw_one_input_present_custom(input_param, unique_name)
                return False

    def _draw_function_inputs(self, unique_name: str) -> bool:
        changed = False

        if len(self._function_node.function_with_gui.inputs_with_gui) > 0:
            if self._can_collapse_inputs():
                changed, self._inputs_expanded = fiat_widgets.node_collapsing_separator(
                    self._node_id, text="Params", expanded=self._inputs_expanded
                )
                if changed:
                    for k, v in self._show_input_details.items():
                        # We do not change the status of nodes that have a link
                        # (since they are hidden by default in the inputs, visible by default in the outputs)
                        has_link = self._function_node.has_input_link(k)
                        if not has_link:
                            self._show_input_details[k] = self._inputs_expanded
            else:
                self._inputs_expanded = True
                fiat_widgets.node_separator(self._node_id, "Params")

        for input_param in self._function_node.function_with_gui.inputs_with_gui:
            if self._draw_one_input(input_param, unique_name):
                changed = True

        return changed

    def _draw_fiat_internals(self) -> None:
        fn = self._function_node.function_with_gui.f_impl
        if fn is None:
            self._fiat_internals_with_gui = {}
            return

        has_fiat_internals = hasattr(fn, "fiat_internals")
        if not has_fiat_internals:
            self._fiat_internals_with_gui = {}
            return
        fn_fiat_internals: Dict[str, Any] = fn.fiat_internals  # type: ignore
        assert isinstance(fn_fiat_internals, dict)

        expand_changed, self._internals_expanded = fiat_widgets.node_collapsing_separator(
            self._node_id, "Internals", self._internals_expanded
        )

        if not self._internals_expanded:
            return

        # remove old internals
        new_fiat_internals_with_gui = {}
        for name in self._fiat_internals_with_gui:
            if name in fn_fiat_internals:
                new_fiat_internals_with_gui[name] = self._fiat_internals_with_gui[name]
        self._fiat_internals_with_gui = new_fiat_internals_with_gui

        # display the internals
        for name, data_with_gui in fn_fiat_internals.items():
            if name not in self._fiat_internals_with_gui:
                self._fiat_internals_with_gui[name] = data_with_gui
            with imgui_ctx.push_obj_id(data_with_gui):
                with imgui_ctx.begin_horizontal("internal_header"):
                    imgui.text(name)
                    imgui.spring()
                    self._show_internals_details[name] = _my_collapsible_button(
                        self._show_internals_details.get(name, False), "internal details"
                    )
                if self._show_internals_details[name]:
                    if data_with_gui.can_present_custom():
                        assert data_with_gui.callbacks.present_custom is not None
                        data_with_gui.callbacks.present_custom()
                    else:
                        as_str = data_with_gui.datatype_value_to_str(data_with_gui.value)
                        imgui.text(as_str)

    def draw_node(self, unique_name: str) -> None:
        with imgui_ctx.push_obj_id(self._function_node):
            with ed_ctx.begin_node(self._node_id):
                with imgui_ctx.begin_vertical("node_content"):
                    # Title and doc
                    with imgui_ctx.begin_horizontal("Title"):
                        self._draw_title(unique_name)
                    imgui.dummy(ImVec2(hello_imgui.em_size(get_fiat_config().style.node_minimum_width_em), 1))

                    # Inputs
                    inputs_changed = self._draw_function_inputs(unique_name)
                    if inputs_changed:
                        self._function_node.function_with_gui.dirty = True
                        if self._function_node.function_with_gui.invoke_automatically:
                            self._function_node.invoke_function()

                    # Internals
                    self._draw_fiat_internals()

                    #
                    # Outputs
                    #

                    # Outputs separator
                    output_separator_str = (
                        "Outputs" if len(self._function_node.function_with_gui.outputs_with_gui) > 1 else "Output"
                    )
                    if self._can_collapse_outputs():
                        changed, self._outputs_expanded = fiat_widgets.node_collapsing_separator(
                            self._node_id, text=output_separator_str, expanded=self._outputs_expanded
                        )
                        if changed:
                            for i, v in self._show_output_details.items():
                                self._show_output_details[i] = self._outputs_expanded
                    else:
                        self._outputs_expanded = True
                        fiat_widgets.node_separator(self._node_id, output_separator_str)

                    # Invoke options
                    with imgui_ctx.begin_horizontal("invoke_options"):
                        imgui.spring()
                        self._draw_invoke_options()

                    # Exceptions, if any
                    self._draw_exception_message()

                    # Outputs
                    self._draw_function_outputs(unique_name)
            self._node_size = ed.get_node_size(self._node_id)

    # ------------------------------------------------------------------------------------------------------------------
    # Save and load user settings
    # ------------------------------------------------------------------------------------------------------------------
    def save_gui_options_to_json(self) -> JsonDict:
        r = {
            "_show_input_details": self._show_input_details,
            "_inputs_expanded": self._inputs_expanded,
            "_show_output_details": self._show_output_details,
            "_outputs_expanded": self._outputs_expanded,
            "_show_internals_details": self._show_internals_details,
            "_internals_expanded": self._internals_expanded,
        }
        return r

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        show_input_details_as_dict_str_bool = json_data.get("_show_input_details")
        if show_input_details_as_dict_str_bool is not None:
            for k, v in show_input_details_as_dict_str_bool.items():
                self._show_input_details[k] = v

        show_output_details_as_dict_str_bool = json_data.get("_show_output_details")
        if show_output_details_as_dict_str_bool is not None:
            for k, v in show_output_details_as_dict_str_bool.items():
                self._show_output_details[int(k)] = v

        show_internals_details_as_dict_str_bool = json_data.get("_show_internals_details")
        if show_internals_details_as_dict_str_bool is not None:
            for k, v in show_internals_details_as_dict_str_bool.items():
                self._show_internals_details[k] = v

        self._inputs_expanded = json_data.get("_inputs_expanded", True)
        self._outputs_expanded = json_data.get("_outputs_expanded", True)
        self._internals_expanded = json_data.get("_internals_expanded", True)


# ------------------------------------------------------------------------------------------------------------------
# Sandbox
# ------------------------------------------------------------------------------------------------------------------
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
        fiat_osd._fiat_osd.render()

    immapp.run(gui, with_node_editor=True, window_title="function_node_gui_sandbox")


if __name__ == "__main__":
    sandbox()
