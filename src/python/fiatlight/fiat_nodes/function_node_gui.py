from __future__ import annotations
from fiatlight.fiat_types import Error, Unspecified, UnspecifiedValue, BoolFunction, JsonDict, ErrorValue
from fiatlight.fiat_core import FunctionNode, FunctionNodeLink, AnyDataWithGui
from fiatlight.fiat_config import FiatColorType, get_fiat_config
from fiatlight.fiat_core.function_with_gui import ParamWithGui
from imgui_bundle import (
    imgui,
    imgui_node_editor as ed,
    ImVec2,
    imgui_ctx,
    hello_imgui,
    imgui_node_editor_ctx as ed_ctx,
)
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx, fiat_osd, collapsible_button
from fiatlight import fiat_widgets
from typing import Dict, List, Any
from dataclasses import dataclass


class FunctionNodeGui:
    """The GUI representation as a visual node for a FunctionNode

    This class is responsible for drawing the node, and for handling the user interactions.
    It is the main GUI class with which the user interacts.
    """

    # ==================================================================================================================
    #                                            Members
    #                                       (All are private)
    # ==================================================================================================================

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

    _function_doc: _FunctionDocElements

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

    # ==================================================================================================================
    #                                            Constructor
    # ==================================================================================================================
    @staticmethod
    def _Constructor_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def __init__(self, function_node: FunctionNode) -> None:
        self._function_node = function_node

        self._node_id = ed.NodeId.create()

        self._pins_input = {}
        for input_name in self._function_node.function_with_gui.all_inputs_names():
            self._pins_input[input_name] = ed.PinId.create()

        self._pins_output = {}
        for i in range(self._function_node.function_with_gui.nb_outputs()):
            self._pins_output[i] = ed.PinId.create()

        self._show_input_details = {
            input_name: False for input_name in self._function_node.function_with_gui.all_inputs_names()
        }
        self._show_output_details = {i: True for i in range(self._function_node.function_with_gui.nb_outputs())}

        self._fill_function_doc()
        self._fiat_internals_with_gui = {}

    # ==================================================================================================================
    #                                            Node info
    #                           (i.e. imgui-node-editor node id, size, etc.)
    # ==================================================================================================================
    @staticmethod
    def _Node_Info_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def node_id(self) -> ed.NodeId:
        return self._node_id

    def node_size(self) -> ImVec2:
        assert self._node_size is not None
        return self._node_size

    # ==================================================================================================================
    #                                            Doc
    # ==================================================================================================================
    @staticmethod
    def _Doc_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def _fill_function_doc(self) -> None:
        self._function_doc = _FunctionDocElements()
        fn_doc = self._function_node.function_with_gui.get_function_doc()
        if fn_doc is not None:
            first_line = fn_doc.split("\n")[0]
            title_line = self._function_node.function_with_gui.name + "(): " + first_line
            remaining_text = fn_doc[len(first_line) :]  # noqa
            self._function_doc.title = title_line
            self._function_doc.doc = remaining_text
        self._function_doc.source_code = self._function_node.function_with_gui.get_function_source_code()

    def _has_doc(self) -> bool:
        return self._function_doc.has_info()

    # ------------------------------------------------------------------------------------------------------------------
    #  Utilities
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _Utilities_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    @staticmethod
    def _call_gui_present_custom(value_with_gui: AnyDataWithGui[Any]) -> None:
        value = value_with_gui.value
        fn_present = value_with_gui.callbacks.present_custom
        if not value_with_gui.can_present_custom():
            return
        assert not isinstance(value, (Error, Unspecified))
        assert fn_present is not None
        fn_present()

    def input_pin_to_param_name(self, pin_id: ed.PinId) -> str | None:
        for k, v in self._pins_input.items():
            if v == pin_id:
                return k
        return None

    def output_pin_to_output_idx(self, pin_id: ed.PinId) -> int | None:
        for k, v in self._pins_output.items():
            if v == pin_id:
                return k
        return None

    def get_function_node(self) -> FunctionNode:
        return self._function_node

    def nb_outputs_with_custom_present(self) -> int:
        r = 0
        nb_outputs = self._function_node.function_with_gui.nb_outputs()
        for i in range(nb_outputs):
            if self._function_node.function_with_gui.output(i).can_present_custom():
                r += 1
        return r

    # ==================================================================================================================
    #                                            Draw the node
    #         This is the heart of the class, with `draw_node` being the main function
    # ==================================================================================================================
    @staticmethod
    def _Draw_Node_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def draw_node(self, unique_name: str) -> None:
        with imgui_ctx.push_obj_id(self._function_node):
            with ed_ctx.begin_node(self._node_id):
                with imgui_ctx.begin_vertical("node_content"):
                    # Title and doc
                    with imgui_ctx.begin_horizontal("Title"):
                        self._draw_title(unique_name)
                    # Set minimum width
                    imgui.dummy(ImVec2(hello_imgui.em_size(get_fiat_config().style.node_minimum_width_em), 1))
                    # Inputs
                    inputs_changed = self._draw_function_inputs(unique_name)
                    if inputs_changed:
                        self._function_node.function_with_gui._dirty = True
                        if self._function_node.function_with_gui.invoke_automatically:
                            self._function_node.invoke_function()
                    # Internals
                    self._draw_fiat_internals()
                    # Exceptions, if any
                    self._draw_exception_message()
                    # Outputs
                    self._draw_function_outputs(unique_name)
            self._node_size = ed.get_node_size(self._node_id)

    # ------------------------------------------------------------------------------------------------------------------
    #  Draw title and header lines
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _Draw_Title_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def _draw_title(self, unique_name: str) -> None:
        fn_name = self._function_node.function_with_gui.name
        imgui.text(fn_name)
        if unique_name != fn_name:
            imgui.text(f" (id: {unique_name})")

        self._render_function_doc(unique_name)

    @staticmethod
    def _show_copy_to_clipboard_button(data_with_gui: AnyDataWithGui[Any]) -> None:
        if not data_with_gui.callbacks.clipboard_copy_possible:
            return
        if data_with_gui.value is UnspecifiedValue or data_with_gui.value is ErrorValue:
            return
        with fontawesome_6_ctx():
            if imgui.button(icons_fontawesome_6.ICON_FA_COPY):
                clipboard_str = data_with_gui.datatype_value_to_clipboard_str()
                imgui.set_clipboard_text(clipboard_str)
            fiat_osd.set_widget_tooltip("Copy value to clipboard")

    def _draw_output_header_line(self, idx_output: int) -> None:
        header_elements = self._output_header_elements(idx_output)

        # If multiple outputs, show "Output X:"
        if self._function_node.function_with_gui.nb_outputs() > 1:
            imgui.text(f"Output {idx_output}:")

        # Show one line value
        if header_elements.value_as_str is not None:
            with imgui_ctx.push_style_color(
                imgui.Col_.text.value, get_fiat_config().style.colors[header_elements.value_color]
            ):
                fiat_widgets.text_maybe_truncated(
                    header_elements.value_as_str,
                    max_width_chars=40,
                    max_lines=1,
                    info_tooltip=header_elements.value_tooltip,
                )

        # Align to the right
        imgui.spring()

        # Copy to clipboard button
        self._show_copy_to_clipboard_button(self._function_node.function_with_gui.output(idx_output))

        # Show present button, if a custom present callback is available
        if header_elements.show_details_button:
            self._show_output_details[idx_output] = collapsible_button(
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
                            if tooltip_str != "":
                                fiat_osd.set_widget_tooltip(tooltip_str)

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
                            if tooltip_str != "":
                                fiat_osd.set_widget_tooltip(tooltip_str)

                    # Param name
                    if header_elements.param_name is not None:
                        imgui.text(header_elements.param_name)

        if header_elements.value_as_str is not None:
            with imgui_ctx.push_style_color(
                imgui.Col_.text.value, get_fiat_config().style.colors[header_elements.param_value_color]
            ):
                fiat_widgets.text_maybe_truncated(
                    header_elements.value_as_str,
                    max_width_chars=40,
                    max_lines=1,
                    info_tooltip=header_elements.param_value_tooltip,
                )

        imgui.spring()

        # Copy to clipboard button
        self._show_copy_to_clipboard_button(input_param.data_with_gui)

        if header_elements.show_details_button:
            self._show_input_details[input_name] = collapsible_button(
                self._show_input_details[input_name], header_elements.details_button_tooltip
            )

        imgui.end_horizontal()

    def _output_header_elements(self, output_idx: int) -> _OutputHeaderLineElements:
        """Return the elements to be presented in a header line"""
        assert 0 <= output_idx < self._function_node.function_with_gui.nb_outputs()

        output_with_gui = self._function_node.function_with_gui.output(output_idx)
        r = _OutputHeaderLineElements()

        # fill r.value_as_str and output_pin_color
        value = output_with_gui.value
        if isinstance(value, Unspecified):
            r.value_as_str = "Unspecified!"
        elif isinstance(value, Error):
            r.value_as_str = "Error!"
        else:
            r.value_as_str = output_with_gui.datatype_value_to_str(value)

        # fill r.status_icon and r.status_icon_tooltips
        has_output_links = len(self._function_node.output_links_for_idx(output_idx)) > 0
        if has_output_links:
            r.status_icon = icons_fontawesome_6.ICON_FA_LINK
            r.status_icon_tooltips = self._function_node.output_node_links_info(output_idx)
        else:
            r.status_icon = icons_fontawesome_6.ICON_FA_PLUG_CIRCLE_XMARK
            r.status_icon_tooltips = ["Unlinked output!"]

        # fill r.output_pin_color
        if has_output_links:
            r.output_pin_color = FiatColorType.OutputPinLinked
        else:
            r.output_pin_color = FiatColorType.OutputPinNotLinked

        # fill r.value_color, and r.value_tooltip
        is_dirty = self._function_node.function_with_gui.is_dirty()
        if isinstance(value, Error):
            r.value_color = FiatColorType.OutputValueWithError
            r.value_tooltip = "Error!"
        elif is_dirty:
            r.value_color = FiatColorType.OutputValueDirty
            r.value_tooltip = "This output is outdated! Please refresh the function."
        elif isinstance(value, Unspecified):
            r.value_color = FiatColorType.OutputValueUnspecified
            r.value_tooltip = "Unspecified!"
        else:
            r.value_color = FiatColorType.OutputValueOk
            r.value_tooltip = "This output is up-to-date"

        # fill r.show_details_button and r.details_button_tooltip
        can_present = output_with_gui.can_present_custom()
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

        # fill value_as_str, status_icon, status_icon_tooltips
        if isinstance(input_param.data_with_gui.value, Error):
            r.status_icon = icons_fontawesome_6.ICON_FA_BOMB
            r.status_icon_tooltips.append("Error!")
            r.value_as_str = "Error!"
        elif isinstance(input_param.data_with_gui.value, Unspecified):
            if isinstance(input_param.default_value, Unspecified):
                r.status_icon = icons_fontawesome_6.ICON_FA_CIRCLE_EXCLAMATION
                r.status_icon_tooltips.append("Unspecified!")
                r.value_as_str = "Unspecified!"
            else:
                r.status_icon = icons_fontawesome_6.ICON_FA_PLUG_CIRCLE_XMARK
                r.status_icon_tooltips.append("Unspecified! Using default value.")
                r.value_as_str = input_param.data_with_gui.datatype_value_to_str(input_param.default_value)
        else:
            r.value_as_str = input_param.data_with_gui.datatype_value_to_str(input_param.data_with_gui.value)

        # fill r.input_pin_color
        if has_link:
            r.input_pin_color = FiatColorType.InputPinLinked
        else:
            r.input_pin_color = FiatColorType.InputPinNotLinked

        # fill r.param_value_color and param_value_tooltip
        if isinstance(input_param.data_with_gui.value, Error):
            r.param_value_color = FiatColorType.ParameterValueWithError
            if has_link:
                r.param_value_tooltip = "Caller transmitted an error!"
            else:
                r.param_value_tooltip = "Error!"
        elif has_link:
            if isinstance(input_param.data_with_gui.value, Unspecified):
                r.param_value_color = FiatColorType.ParameterValueUnspecified
                r.param_value_tooltip = "Caller transmitted an unspecified value!"
            else:
                r.param_value_color = FiatColorType.ParameterValueLinked
                r.param_value_tooltip = "Received from link"
        elif isinstance(input_param.data_with_gui.value, Unspecified):
            if input_param.default_value is not UnspecifiedValue:
                r.param_value_color = FiatColorType.ParameterValueUsingDefault
                r.param_value_tooltip = "Using default value"
            else:
                r.param_value_color = FiatColorType.ParameterValueUnspecified
                r.param_value_tooltip = "This parameter needs to be specified!"
        else:
            r.param_value_color = FiatColorType.ParameterValueUserSpecified
            r.param_value_tooltip = "User specified value"

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

    # ------------------------------------------------------------------------------------------------------------------
    #       Draw inputs
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _Draw_Inputs_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def _draw_function_inputs(self, unique_name: str) -> bool:
        changed = False

        nb_inputs = self._function_node.function_with_gui.nb_inputs()
        if nb_inputs == 0:
            return False

        nb_unlinked_inputs = self._function_node.nb_unlinked_inputs()

        #
        # Instantiate the node separator parameters
        #
        node_separator_params = fiat_widgets.NodeSeparatorParams()
        node_separator_params.parent_node = self._node_id
        # expanded state
        node_separator_params.expanded = self._inputs_expanded
        # Separator text
        node_separator_params.text = "Params" if nb_inputs > 1 else "Param"
        if nb_unlinked_inputs > 0 and not self._inputs_expanded:
            node_separator_params.text += f" ({nb_unlinked_inputs} hidden)"
        # Separator collapse button
        node_separator_params.show_collapse_button = nb_unlinked_inputs > 0
        # Separator collapse all button
        node_separator_params.show_toggle_collapse_all_button = nb_unlinked_inputs > 1 and self._inputs_expanded

        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)

        # Update the expanded state
        self._inputs_expanded = node_separator_output.expanded

        # Update the inputs expanded state
        if node_separator_output.was_toggle_collapse_all_clicked:
            has_one_visible_input = any(self._show_input_details[input_name] for input_name in self._show_input_details)
            new_state = not has_one_visible_input
            for input_name, expanded in self._show_input_details.items():
                self._show_input_details[input_name] = new_state

        #
        # Draw the inputs
        #
        for param_name in self._function_node.function_with_gui.all_inputs_names():
            input_param = self._function_node.function_with_gui.param(param_name)
            if self._draw_one_input(input_param, unique_name):
                changed = True

        return changed

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
            fiat_osd.show_bool_detached_window_button(btn_label, popup_label, edit_input)

        # Now that we can have a detached view, there are two ways
        # that can change the input value:
        if can_edit_in_node and edit_input():
            # 1. The user edits the input value in this window
            changed = True
        if can_edit_in_popup and fiat_osd.get_detached_window_bool_return(btn_label):
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
            fiat_osd.show_void_detached_window_button("", popup_label, present_input)

        if can_present_custom_in_node:
            present_input()

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
                    fiat_osd.set_widget_tooltip("Unset this parameter.")
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
                        fiat_osd.set_widget_tooltip(value_to_create_tooltip)
                    return set_changed

                return fn_set_unset_with_default_value

            else:
                # For Error or Unspecified values, when no default value is available
                def fn_set_unset_with_no_provider() -> bool:
                    with fontawesome_6_ctx():
                        imgui.button(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION)
                        fiat_osd.set_widget_tooltip("No default value provider!")
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

    # ------------------------------------------------------------------------------------------------------------------
    #       Draw outputs
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _Draw_Outputs_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def _draw_function_outputs(self, unique_name: str) -> None:
        nb_outputs = self._function_node.function_with_gui.nb_outputs()
        nb_unlinked_outputs = self._function_node.nb_unlinked_outputs()

        #
        # Instantiate the node separator parameters
        #
        node_separator_params = fiat_widgets.NodeSeparatorParams()
        node_separator_params.parent_node = self._node_id
        # expanded state
        node_separator_params.expanded = self._outputs_expanded
        # Separator text
        node_separator_params.text = "Outputs" if nb_outputs > 1 else "Output"
        if nb_unlinked_outputs > 0 and not self._outputs_expanded:
            node_separator_params.text += f" ({nb_unlinked_outputs} hidden)"
        # show collapse button
        node_separator_params.show_collapse_button = nb_unlinked_outputs > 0
        # show collapse all button
        node_separator_params.show_toggle_collapse_all_button = (
            self._outputs_expanded and self.nb_outputs_with_custom_present() > 0
        )

        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)

        # Update the expanded state
        self._outputs_expanded = node_separator_output.expanded
        # If the collapse all button was clicked, we update the state of all outputs
        if node_separator_output.was_toggle_collapse_all_clicked:
            has_one_visible_output = any(self._show_output_details[i] for i in range(nb_outputs))
            new_state = not has_one_visible_output
            for i in range(nb_outputs):
                self._show_output_details[i] = new_state

        # Invoke options
        with imgui_ctx.begin_horizontal("invoke_options"):
            imgui.spring()
            self._draw_invoke_options()

        # Outputs
        for idx_output in range(self._function_node.function_with_gui.nb_outputs()):
            has_link = len(self._function_node.output_links_for_idx(idx_output)) > 0
            if not has_link and not self._outputs_expanded:
                continue
            with imgui_ctx.begin_group():
                self._draw_one_output(idx_output, unique_name)

    def _draw_one_output(self, idx_output: int, unique_name: str) -> None:
        output_param = self._function_node.function_with_gui.output(idx_output)
        with imgui_ctx.push_obj_id(output_param):
            with imgui_ctx.begin_horizontal("outputH"):
                self._draw_output_header_line(idx_output)
            can_present = output_param.can_present_custom()
            if can_present and self._show_output_details[idx_output]:
                # capture the output_param for the lambda
                # (otherwise, the lambda would capture the last output_param in the loop)
                output_param_captured = output_param

                def present_output() -> None:
                    # Present output can be called either directly in this window or in a detached window
                    self._call_gui_present_custom(output_param_captured)

                callbacks = output_param.callbacks
                can_present_custom_in_node = not callbacks.present_custom_popup_required
                can_present_custom_in_popup = (
                    callbacks.present_custom_popup_required or callbacks.present_custom_popup_possible
                )

                if can_present_custom_in_popup:
                    btn_label = "##present_custom_in_popup"  # This will be our popup id (with the imgui id context)
                    popup_label = f"detached view - {unique_name}: output {idx_output}"
                    fiat_osd.show_void_detached_window_button(btn_label, popup_label, present_output)

                if can_present_custom_in_node:
                    present_output()

    def _draw_invoke_options(self) -> None:
        fn_with_gui = self._function_node.function_with_gui
        btn_size = hello_imgui.em_to_vec2(4, 0)

        with fontawesome_6_ctx():
            if fn_with_gui.invoke_automatically_can_set:
                invoke_changed, fn_with_gui.invoke_automatically = imgui.checkbox(
                    "##Auto refresh", self._function_node.function_with_gui.invoke_automatically
                )
                fiat_osd.set_widget_tooltip("Tick to invoke automatically.")
                if invoke_changed and fn_with_gui.invoke_automatically:
                    self._function_node.invoke_function()

            if fn_with_gui.is_dirty():
                if imgui.button(icons_fontawesome_6.ICON_FA_ROTATE, btn_size):
                    self._function_node.invoke_function()
                fiat_osd.set_widget_tooltip("Refresh needed! Click to refresh.")

            if not fn_with_gui.invoke_automatically:
                if not fn_with_gui.is_dirty():
                    imgui.text(icons_fontawesome_6.ICON_FA_CHECK)
                    fiat_osd.set_widget_tooltip("Up to date!")
                else:
                    imgui.text(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION)
                    fiat_osd.set_widget_tooltip("Refresh needed!")

    # ------------------------------------------------------------------------------------------------------------------
    #      Draw Internals
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _Draw_Internals_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

    def _draw_fiat_internals(self) -> None:
        fn = self._function_node.function_with_gui._f_impl  # noqa
        if fn is None:
            self._fiat_internals_with_gui = {}
            return

        has_fiat_internals = hasattr(fn, "fiat_internals")
        if not has_fiat_internals:
            self._fiat_internals_with_gui = {}
            return
        fn_fiat_internals: Dict[str, Any] = fn.fiat_internals  # type: ignore
        assert isinstance(fn_fiat_internals, dict)

        # Separator

        #
        # Instantiate the node separator parameters
        #
        node_separator_params = fiat_widgets.NodeSeparatorParams()
        node_separator_params.parent_node = self._node_id
        node_separator_params.expanded = self._internals_expanded
        node_separator_params.text = "Internals"
        node_separator_params.show_collapse_button = True
        node_separator_params.show_toggle_collapse_all_button = True
        if not self._internals_expanded:
            node_separator_params.text += f" ({len(fn_fiat_internals)} hidden)"

        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)

        # Update the expanded state
        self._internals_expanded = node_separator_output.expanded

        # Update the internals expanded state
        if node_separator_output.was_toggle_collapse_all_clicked:
            has_one_visible_internal = any(self._show_internals_details[name] for name in self._show_internals_details)
            new_state = not has_one_visible_internal
            for name, expanded in self._show_internals_details.items():
                self._show_internals_details[name] = new_state

        # remove old internals
        new_fiat_internals_with_gui = {}
        for name in self._fiat_internals_with_gui:
            if name in fn_fiat_internals:
                new_fiat_internals_with_gui[name] = self._fiat_internals_with_gui[name]
        self._fiat_internals_with_gui = new_fiat_internals_with_gui

        if not self._internals_expanded:
            return

        # display the internals
        for name, data_with_gui in fn_fiat_internals.items():
            if name not in self._fiat_internals_with_gui:
                self._fiat_internals_with_gui[name] = data_with_gui
            with imgui_ctx.push_obj_id(data_with_gui):
                with imgui_ctx.begin_horizontal("internal_header"):
                    imgui.text(name)
                    imgui.spring()
                    self._show_internals_details[name] = collapsible_button(
                        self._show_internals_details.get(name, False), "internal details"
                    )
                if self._show_internals_details[name]:
                    if data_with_gui.can_present_custom():
                        assert data_with_gui.callbacks.present_custom is not None
                        data_with_gui.callbacks.present_custom()
                    else:
                        as_str = data_with_gui.datatype_value_to_str(data_with_gui.value)
                        imgui.text(as_str)

    # ------------------------------------------------------------------------------------------------------------------
    #      Draw misc elements
    # ------------------------------------------------------------------------------------------------------------------
    def _draw_exception_message(self) -> None:
        last_exception_message = self._function_node.function_with_gui.get_last_exception_message()
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
            color=get_fiat_config().style.colors[FiatColorType.ExceptionError],
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
                    self._function_node.function_with_gui._dirty = True
                    self._function_node.function_with_gui.invoke()
                    imgui.close_current_popup()  # close the popup (which will never happen, we will crash)
                imgui.same_line()

            popup_flags = imgui.WindowFlags_.always_auto_resize.value
            fiat_osd.show_void_detached_window_button(
                btn_label, popup_label, confirmation_gui, window_flags=popup_flags
            )

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
            fiat_osd.show_void_detached_window_button(btn_text, popup_label, show_doc)

    # ==================================================================================================================
    # Save and load user settings
    # ==================================================================================================================
    @staticmethod
    def _Save_Load_User_Settings_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        pass

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
            if f._function_node.function_with_gui == function_node_link.src_function_node.function_with_gui:  # noqa
                self.start_id = f._pins_output[function_node_link.src_output_idx]  # noqa
            if f._function_node.function_with_gui == function_node_link.dst_function_node.function_with_gui:  # noqa
                self.end_id = f._pins_input[function_node_link.dst_input_name]  # noqa
        assert hasattr(self, "start_id")
        assert hasattr(self, "end_id")

    def draw(self) -> None:
        ed.link(self.link_id, self.start_id, self.end_id)


@dataclass
class _InputParamHeaderLineElements:
    """Data to be presented in a header line"""

    input_pin_color: FiatColorType = FiatColorType.InputPinNotLinked

    status_icon: str | None = None
    status_icon_tooltips: List[str] | None = None

    param_name: str | None = None
    param_value_color: FiatColorType = FiatColorType.ParameterValueUsingDefault
    param_value_tooltip: str | None = None

    value_as_str: str | None = None

    show_details_button: bool = False
    details_button_tooltip: str = ""


class _OutputHeaderLineElements:
    """Data to be presented in a header line"""

    output_pin_color: FiatColorType = FiatColorType.OutputPinLinked

    status_icon: str | None = None
    status_icon_tooltips: List[str] | None = None

    value_as_str: str | None = None
    value_color: FiatColorType = FiatColorType.OutputValueOk
    value_tooltip: str | None = None

    show_details_button: bool = False
    details_button_tooltip: str = ""


@dataclass
class _FunctionDocElements:
    title: str | None = None
    doc: str | None = None
    source_code: str | None = None

    def has_info(self) -> bool:
        return self.title is not None or self.doc is not None or self.source_code is not None


# ==================================================================================================================
# Sandbox
# ==================================================================================================================
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

    function_with_gui = to_function_with_gui(add)
    function_node = FunctionNode(function_with_gui)
    function_node_gui = FunctionNodeGui(function_node)

    def gui() -> None:
        with ed_ctx.begin("Functions Graph"):
            function_node_gui.draw_node("add")
        fiat_osd._render_all_osd()  # noqa

    immapp.run(gui, with_node_editor=True, window_title="function_node_gui_sandbox")


if __name__ == "__main__":
    sandbox()
