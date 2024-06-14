"""FunctionNodeGui represents the GUI for a FunctionNode

In summary, the FunctionNodeGui manages the GUI for a FunctionNode: it provides methods for drawing the node's GUI,
interacting with the node's inputs and outputs, and saving and loading the GUI's state.
It is responsible for interacting with imgui-node-editor, and for handling the user interactions.

Notes:
    - high-level overview of the classes involved:

        FunctionNodeGui *--- FunctionNode *--- FunctionWithGui
           (i.e. FunctionNodeGui includes 1 FunctionNode, and FunctionNode includes 1 FunctionWithGui)

        FunctionsGraph *--many- FunctionNode
        FunctionsGraph *--many- FunctionNodeLink
          (i.e. FunctionsGraph includes many FunctionNode, and many FunctionNodeLink)

        FunctionGraphGui *-- FunctionsGraph
        FunctionGraphGui *--many- FunctionNodeGui
            (i.e. FunctionGraphGui includes 1 FunctionsGraph, and many FunctionNodeGui)


    - `FunctionWithGui` is a class that wraps a function and provides GUI for its inputs and outputs
          The inputs and outputs are represented as instances of AnyDataWithGui, which also stores the GUI callbacks.
    - `FunctionNode` is a node in the "symbolic" functions graph.
        It contains a FunctionWithGui, and links to other nodes. It is not able to draw itself.
    - `FunctionNodeGui` is a node in the "visual" function graph, handled by imgui-node-editor.
         It is able to draw itself, and to handle user interactions. It contains a FunctionNode.

"""

from __future__ import annotations

import fiatlight
from fiatlight.fiat_types import Error, Unspecified, UnspecifiedValue, JsonDict
from fiatlight.fiat_core import FunctionNode, FunctionNodeLink, AnyDataWithGui
from fiatlight.fiat_core.any_data_with_gui import GuiHeaderLineParams
from fiatlight.fiat_config import FiatColorType, get_fiat_config
from fiatlight.fiat_core.param_with_gui import ParamWithGui
from imgui_bundle import (
    imgui,
    imgui_node_editor as ed,
    ImVec2,
    imgui_ctx,
    hello_imgui,
    imgui_node_editor_ctx as ed_ctx,
    imspinner,
)
from imgui_bundle import ImColor
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx, fiat_osd
from fiatlight import fiat_widgets, fiat_togui
from typing import Dict, List, Any
from dataclasses import dataclass


_CURRENT_FUNCTION_NODE_ID: ed.NodeId | None = None


def get_current_function_node_id() -> ed.NodeId | None:
    return _CURRENT_FUNCTION_NODE_ID


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

    # Fine tune function internals
    # (displayed if the user adds a *function variable* dictionary named fiat_tuning)
    _fiat_tuning_with_gui: Dict[str, AnyDataWithGui[Any]]

    # user settings:
    #   Flags that indicate whether the details of the inputs/outputs/internals are shown or not
    #   (those settings are saved in the user settings file)
    _inputs_expanded: bool = True
    _outputs_expanded: bool = True
    fiat_tuning_expanded: bool = False  # This is for the debug internals
    _internal_state_gui_expanded: bool = True  # This is for the function's internal state gui

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

        for input_name in self._function_node.function_with_gui.all_inputs_names():
            param = self._function_node.function_with_gui.param(input_name)
            if self._function_node.has_input_link(input_name):
                param.data_with_gui._expanded = False  # No need to expand linked field by default

        self._fill_function_docstring_and_source()
        self._fiat_tuning_with_gui = {}

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

    @staticmethod
    def _Doc_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ==================================================================================================================
        #                                            Doc
        # ==================================================================================================================
        """
        pass

    def _fill_function_docstring_and_source(self) -> None:
        self._function_doc = _FunctionDocElements()
        self._function_doc.source_code = self._function_node.function_with_gui.get_function_source_code()
        self._function_doc.userdoc = self._function_node.function_with_gui.get_function_userdoc()
        self._function_doc.userdoc_is_markdown = self._function_node.function_with_gui.doc_markdown

    def _has_doc(self) -> bool:
        return self._function_doc.has_info()

    @staticmethod
    def _Utilities_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #  Utilities
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    def _heartbeat(self) -> bool:
        needs_refresh = self._function_node.heartbeat()
        return needs_refresh

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
            if self._function_node.function_with_gui.output(i).can_present():
                r += 1
        return r

    def invoke(self) -> None:
        self._function_node.call_invoke_async_or_not()

    @staticmethod
    def _Draw_Node_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ==================================================================================================================
        #                                            Draw the node
        #         This is the heart of the class, with `draw_node` being the main function
        # ==================================================================================================================
        """
        pass

    def draw_node(self, unique_name: str) -> bool:
        global _CURRENT_FUNCTION_NODE_ID
        inputs_changed: bool
        needs_refresh_for_heartbeat = self._heartbeat()
        with imgui_ctx.push_obj_id(self._function_node):
            with ed_ctx.begin_node(self._node_id):
                _CURRENT_FUNCTION_NODE_ID = self._node_id
                with imgui_ctx.begin_vertical("node_content" + unique_name):
                    # Title and doc
                    with imgui_ctx.begin_horizontal("Title"):
                        self._draw_title(unique_name)
                    # Set minimum width
                    imgui.dummy(ImVec2(hello_imgui.em_size(get_fiat_config().style.node_minimum_width_em), 1))

                    # Inputs
                    inputs_changed = self._draw_function_inputs(unique_name)
                    # Function internal state
                    internal_state_changed = self._draw_function_internal_state(unique_name)

                    if inputs_changed or internal_state_changed or needs_refresh_for_heartbeat:
                        self._function_node.on_inputs_changed()

                    # Internals
                    self._draw_fiat_tuning()
                    # Exceptions, if any
                    self._draw_exception_message()
                    # Outputs
                    self._draw_function_outputs(unique_name)
            self._node_size = ed.get_node_size(self._node_id)
        return inputs_changed

    @staticmethod
    def _Draw_Title_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #  Draw title and header lines
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    def _draw_title(self, unique_name: str) -> None:
        fn_name = self._function_node.function_with_gui.name
        imgui.text(fn_name)
        if unique_name != fn_name:
            imgui.text(f" (id: {unique_name})")

        self._draw_async_status()
        self._render_function_doc(unique_name)

    def _draw_async_status(self) -> None:
        if self._function_node.is_running_async():
            color = ImColor(1.0, 1.0, 0.0, 1.0)
            radius1 = imgui.get_font_size() / 3.5
            imgui.spring()
            imspinner.spinner_ang_triple(
                "spinner_ang_triple",
                radius1,
                radius1 * 1.2,
                radius1 * 2.0,
                2.9,
                color,
                color,
                color,
            )
            fiat_osd.set_widget_tooltip("Running...")

    def _draw_output_pin(self, header_elements: _OutputHeaderLineElements, idx_output: int) -> None:
        if not fiatlight.is_rendering_in_node():
            return
        # Show colored pin with possible tooltip
        with imgui_ctx.push_style_color(
            imgui.Col_.text.value,
            get_fiat_config().style.color_as_vec4(header_elements.output_pin_color),
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

    def _draw_input_pin(self, header_elements: _InputParamHeaderLineElements) -> None:
        if not fiatlight.is_rendering_in_node():
            return
        with imgui_ctx.push_style_color(
            imgui.Col_.text.value, get_fiat_config().style.color_as_vec4(header_elements.input_pin_color)
        ):
            input_name = header_elements.param_name
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

    def _output_header_elements(self, output_idx: int) -> _OutputHeaderLineElements:
        """Return the elements to be presented in a header line"""
        assert 0 <= output_idx < self._function_node.function_with_gui.nb_outputs()

        output_with_gui = self._function_node.function_with_gui.output(output_idx)
        r = _OutputHeaderLineElements()

        # fill r.value_as_str and output_pin_color
        value = output_with_gui.value

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

        # fill r.value_color, and r.label_tooltip
        is_dirty = self._function_node.function_with_gui.is_dirty()
        if isinstance(value, Error):
            r.value_color = FiatColorType.ValueWithError
            r.value_tooltip = "Error!"
        elif is_dirty:
            r.value_color = FiatColorType.OutputValueDirty
            r.value_tooltip = "This output is outdated! Please refresh the function."
        elif isinstance(value, Unspecified):
            r.value_color = FiatColorType.ValueUnspecified
            r.value_tooltip = "Unspecified!"
        else:
            r.value_color = FiatColorType.OutputValueOk
            r.value_tooltip = "This output is up-to-date"

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
        elif isinstance(input_param.data_with_gui.value, Unspecified):
            if isinstance(input_param.default_value, Unspecified):
                r.status_icon = icons_fontawesome_6.ICON_FA_CIRCLE_EXCLAMATION
                r.status_icon_tooltips.append("Unspecified!")
            else:
                r.status_icon = icons_fontawesome_6.ICON_FA_PLUG_CIRCLE_XMARK
                r.status_icon_tooltips.append("Unspecified! Using default value.")

        # fill r.input_pin_color
        if has_link:
            r.input_pin_color = FiatColorType.InputPinLinked
        else:
            r.input_pin_color = FiatColorType.InputPinNotLinked

        # fill r.param_label_color and param_label_tooltip
        if isinstance(input_param.data_with_gui.value, Error):
            r.param_label_color = FiatColorType.ParameterValueWithError
            if has_link:
                r.param_label_tooltip = "Caller transmitted an error!"
            else:
                r.param_label_tooltip = "Error!"
        elif has_link:
            if isinstance(input_param.data_with_gui.value, Unspecified):
                r.param_label_color = FiatColorType.ParameterValueUnspecified
                r.param_label_tooltip = "Caller transmitted an unspecified value!"
            else:
                r.param_label_color = FiatColorType.ParameterValueLinked
                r.param_label_tooltip = "Received from link"
        elif isinstance(input_param.data_with_gui.value, Unspecified):
            if input_param.default_value is not UnspecifiedValue:
                r.param_label_color = FiatColorType.ParameterValueUsingDefault
                r.param_label_tooltip = "Using default value"
            else:
                r.param_label_color = FiatColorType.ParameterValueUnspecified
                r.param_label_tooltip = "This parameter needs to be specified!"
        else:
            r.param_label_color = FiatColorType.ParameterValueUserSpecified
            r.param_label_tooltip = None

        # fill param_name and param_name_tooltip
        r.param_name = input_param.name

        return r

    @staticmethod
    def _Draw_Inputs_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #       Draw inputs
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    def _draw_function_inputs(self, unique_name: str) -> bool:
        shall_disable_input = (
            self._function_node.is_running_async() and get_fiat_config().run_config.disable_input_during_execution
        )
        if shall_disable_input:
            imgui.begin_disabled()

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
            self._function_node.function_with_gui.toggle_expand_inputs()

        #
        # Draw the inputs
        #
        for param_name in self._function_node.function_with_gui.all_inputs_names():
            input_param = self._function_node.function_with_gui.param(param_name)
            if self._draw_one_input(input_param, unique_name):
                changed = True

        if shall_disable_input:
            imgui.end_disabled()

        return changed

    def _draw_one_input(self, input_param: ParamWithGui[Any], unique_name: str) -> bool:
        with imgui_ctx.push_obj_id(input_param):
            input_name = input_param.name

            has_link = self._function_node.has_input_link(input_name)
            if not has_link and not self._inputs_expanded:
                return False

            can_edit = not has_link

            header_elements = self._input_param_header_elements(input_param)

            input_param.data_with_gui.label_color = get_fiat_config().style.color_as_vec4(
                header_elements.param_label_color
            )
            input_param.data_with_gui.status_tooltip = header_elements.param_label_tooltip

            header_params = GuiHeaderLineParams[Any]()
            header_params.prefix_gui = lambda: self._draw_input_pin(header_elements)
            header_params.default_value_if_unspecified = input_param.default_value
            header_params.popup_title = f"detached view - {unique_name}: param {input_param.name}"

            if can_edit:
                changed = input_param.data_with_gui.gui_edit_customizable(header_params)
                return changed
            else:
                input_param.data_with_gui.gui_present_customizable(header_params)
                return False

    @staticmethod
    def _Draw_Outputs_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #       Draw outputs
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    def _draw_function_outputs(self, unique_name: str) -> None:
        nb_outputs = self._function_node.function_with_gui.nb_outputs()
        nb_unlinked_outputs = self._function_node.nb_unlinked_outputs()

        if nb_outputs == 0:
            return

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
            self._function_node.function_with_gui.toggle_expand_outputs()

        # Invoke options
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

        bof_header_elements = self._output_header_elements(idx_output)

        output_param.label_color = get_fiat_config().style.color_as_vec4(bof_header_elements.value_color)
        output_param.status_tooltip = bof_header_elements.value_tooltip

        header_params = GuiHeaderLineParams[Any]()
        header_params.suffix_gui = lambda: self._draw_output_pin(bof_header_elements, idx_output)
        header_params.popup_title = f"detached view - {unique_name}: output {idx_output}"

        output_param.gui_present_customizable(header_params)

    def _draw_invoke_options(self) -> None:
        fn_with_gui = self._function_node.function_with_gui
        if not fn_with_gui.invoke_manually:
            return
        with fontawesome_6_ctx():
            with imgui_ctx.begin_horizontal("invoke_options"):
                btn_size = hello_imgui.em_to_vec2(4, 0)
                # Manual call
                if fn_with_gui.is_invoke_manually_io():
                    imgui.spring()
                    if imgui.button("Call IO manually"):
                        self.invoke()
                    imgui.spring()
                elif fn_with_gui.is_dirty():
                    imgui.spring()
                    is_running_async = self._function_node.is_running_async()
                    imgui.begin_disabled(is_running_async)
                    if imgui.button(icons_fontawesome_6.ICON_FA_ROTATE, btn_size):
                        self.invoke()
                    fiat_osd.set_widget_tooltip("Refresh needed! Click to refresh.")
                    imgui.end_disabled()

                    imgui.text(icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION + " Refresh needed!")
                    fiat_osd.set_widget_tooltip("Refresh needed!")
                    imgui.spring()
                else:
                    imgui.spring()
                    imgui.text(icons_fontawesome_6.ICON_FA_CHECK)
                    fiat_osd.set_widget_tooltip("Up to date!")

    @staticmethod
    def _Draw_Internals_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #      Draw function Internal State and fiat_tuning (debug help)
        # ------------------------------------------------------------------------------------------------------------------
        """
        pass

    def _draw_function_internal_state(self, unique_name: str) -> bool:
        fn_with_gui = self._function_node.function_with_gui
        internal_state_fn = fn_with_gui.internal_state_gui
        if internal_state_fn is None:
            return False

        #
        # Draw the separator
        #
        node_separator_params = fiat_widgets.NodeSeparatorParams()
        node_separator_params.parent_node = self._node_id
        # expanded state
        node_separator_params.expanded = self._internal_state_gui_expanded
        # Separator text
        node_separator_params.text = "Function internal state"
        # Separator collapse button
        node_separator_params.show_collapse_button = True
        # Separator collapse all button
        node_separator_params.show_toggle_collapse_all_button = False
        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)
        # Update the expanded state
        self._internal_state_gui_expanded = node_separator_output.expanded

        #
        # Invoke the internal state gui
        #
        if self._internal_state_gui_expanded:
            result = internal_state_fn()
            return result
        else:
            return False

    def _draw_fiat_tuning(self) -> None:
        """Draw the internals of the function (for debugging)
        They should be stored in a dictionary fiat_tuning inside the function.
        See example inside toon_edges.py
        """
        fn = self._function_node.function_with_gui._f_impl  # noqa
        if fn is None:
            self._fiat_tuning_with_gui = {}
            return

        has_fiat_tuning = hasattr(fn, "fiat_tuning")
        if not has_fiat_tuning:
            self._fiat_tuning_with_gui = {}
            return
        fn_fiat_tuning: Dict[str, Any] = fn.fiat_tuning  # type: ignore
        assert isinstance(fn_fiat_tuning, dict)

        # Separator

        #
        # Instantiate the node separator parameters
        #
        node_separator_params = fiat_widgets.NodeSeparatorParams()
        node_separator_params.parent_node = self._node_id
        node_separator_params.expanded = self.fiat_tuning_expanded
        node_separator_params.text = "Fiat Tuning"
        node_separator_params.show_collapse_button = True
        node_separator_params.show_toggle_collapse_all_button = self.fiat_tuning_expanded
        if not self.fiat_tuning_expanded:
            node_separator_params.text += f" ({len(fn_fiat_tuning)} hidden)"

        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)

        # Update the expanded state
        self.fiat_tuning_expanded = node_separator_output.expanded

        # Update the internals expanded state
        if node_separator_output.was_toggle_collapse_all_clicked:
            from fiatlight.fiat_core.any_data_with_gui import toggle_expanded_state_on_guis

            guis = [gui for _name, gui in self._fiat_tuning_with_gui.items()]
            toggle_expanded_state_on_guis(guis)

        # remove old internals
        new_fiat_tuning_with_gui = {}
        for name in self._fiat_tuning_with_gui:
            if name in fn_fiat_tuning:
                new_fiat_tuning_with_gui[name] = self._fiat_tuning_with_gui[name]
        self._fiat_tuning_with_gui = new_fiat_tuning_with_gui

        if not self.fiat_tuning_expanded:
            return

        # display the internals
        for name, value in fn_fiat_tuning.items():
            # Insert new AnyDataWithGui into self._fiat_tuning_with_gui if needed
            # either by creating an AnyDataWithGui from the value or using the one that is provided
            if name not in self._fiat_tuning_with_gui:
                if not isinstance(value, AnyDataWithGui):
                    self._fiat_tuning_with_gui[name] = fiat_togui.any_type_to_gui(type(value))
                else:
                    self._fiat_tuning_with_gui[name] = value
                self._fiat_tuning_with_gui[name].label = name
            data_with_gui = self._fiat_tuning_with_gui[name]

            # Update value
            if not isinstance(value, AnyDataWithGui):
                data_with_gui.value = value
            else:
                data_with_gui.value = value.value

            # Draw the gui for the internal
            with imgui_ctx.push_obj_id(data_with_gui):
                data_with_gui.gui_present()

    # ------------------------------------------------------------------------------------------------------------------
    #      Draw misc elements
    # ------------------------------------------------------------------------------------------------------------------
    def _draw_exception_message(self) -> None:
        last_exception_message = self._function_node.function_with_gui.get_last_exception_message()
        if last_exception_message is None:
            return

        min_exception_width = hello_imgui.em_size(30)
        exception_width = min_exception_width
        if self._node_size is not None:
            exception_width = self._node_size.x - hello_imgui.em_size(2)
            if exception_width < min_exception_width:
                exception_width = min_exception_width
        fiat_widgets.text_maybe_truncated(
            "Exception:\n" + last_exception_message,
            max_width_pixels=exception_width,
            max_lines=3,
            color=get_fiat_config().style.color_as_vec4(FiatColorType.ExceptionError),
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
                    get_fiat_config().run_config.catch_function_exceptions = False
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

            with imgui_ctx.begin_vertical("function_doc"):
                if self._function_doc.userdoc is not None:
                    with imgui_ctx.begin_horizontal("header"):
                        imgui.spring()
                        imgui.text("User documentation")

                    if self._function_doc.userdoc_is_markdown:
                        imgui_md.render(self._function_doc.userdoc)
                    else:
                        imgui.text_wrapped(self._function_doc.userdoc)
                    imgui.separator()

                if self._function_doc.source_code is not None:
                    md = "### Source code\n\n"
                    md += f"```python\n{self._function_doc.source_code}\n```"
                    imgui_md.render(md)

        with fontawesome_6_ctx():
            imgui.spring()
            popup_label = f"{unique_name}(): function documentation"
            btn_text = icons_fontawesome_6.ICON_FA_BOOK
            fiat_osd.show_void_detached_window_button(btn_text, popup_label, show_doc)

    @staticmethod
    def _Serialization_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # ==================================================================================================================
        # Save and load user settings
        # Note:
        #     save_user_inputs_to_json & load_user_inputs_from_json are not implemented here:
        #     you should use FunctionNode.save_user_inputs_to_json & FunctionNode.load_user_inputs_from_json
        # ==================================================================================================================
        """
        pass

    def save_gui_options_to_json(self) -> JsonDict:
        # We cannot save the fiat_tuning_options, because reloading them
        # would fail: the list of fiat_tuning_options is unknown until the
        # first function execution.
        #     fiat_tuning_options = {}
        #     for name, data_with_gui in self._fiat_tuning_with_gui.items():
        #         fiat_tuning_options[name] = data_with_gui.save_gui_options_to_json()
        r = {
            "_inputs_expanded": self._inputs_expanded,
            "_outputs_expanded": self._outputs_expanded,
            "fiat_tuning_expanded": self.fiat_tuning_expanded,
            "_internal_state_gui_expanded": self._internal_state_gui_expanded,
            "_function_node": self._function_node.save_gui_options_to_json(),
            # "_fiat_tuning_with_gui": fiat_tuning_options,
        }
        return r

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        self._inputs_expanded = json_data.get("_inputs_expanded", True)
        self._outputs_expanded = json_data.get("_outputs_expanded", True)
        self.fiat_tuning_expanded = json_data.get("fiat_tuning_expanded", False)
        self._internal_state_gui_expanded = json_data.get("_internal_state_gui_expanded", True)
        self._function_node.load_gui_options_from_json(json_data["_function_node"])
        # fiat_tuning_options = json_data.get("_fiat_tuning_with_gui", {})
        # for name, data_with_gui in self._fiat_tuning_with_gui.items():
        #     if name in fiat_tuning_options:
        #         data_with_gui.load_gui_options_from_json(fiat_tuning_options[name])


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

    param_name: str = ""
    param_label_color: FiatColorType = FiatColorType.ParameterValueUsingDefault
    param_label_tooltip: str | None = None


class _OutputHeaderLineElements:
    """Data to be presented in a header line"""

    output_pin_color: FiatColorType = FiatColorType.OutputPinLinked

    status_icon: str | None = None
    status_icon_tooltips: List[str] | None = None

    value_color: FiatColorType = FiatColorType.OutputValueOk
    value_tooltip: str | None = None


@dataclass
class _FunctionDocElements:
    source_code: str | None = None
    userdoc: str | None = None
    userdoc_is_markdown: bool = False

    def has_info(self) -> bool:
        return self.source_code is not None or self.userdoc is not None


# ==================================================================================================================
# Sandbox
# ==================================================================================================================
def sandbox() -> None:
    import fiatlight
    from imgui_bundle import immapp
    from enum import Enum

    class MyEnum(Enum):  # noqa
        ONE = 1
        TWO = 2
        THREE = 3

    def add(
        # a: int | None = None,
        e: MyEnum = MyEnum.ONE,
        # x: int = 1,
        # y: int = 2,
        # s: str = "Hello",
    ) -> List[str]:
        return ["Hello", "World", "!"]

    function_with_gui = fiatlight.FunctionWithGui(add)
    function_node = FunctionNode(function_with_gui)
    function_node_gui = FunctionNodeGui(function_node)

    def gui() -> None:
        with ed_ctx.begin("Functions Graph"):
            function_node_gui.draw_node("add")
        fiat_osd._render_all_osd()  # noqa

    immapp.run(gui, with_node_editor=True, window_title="function_node_gui_sandbox")


if __name__ == "__main__":
    sandbox()
