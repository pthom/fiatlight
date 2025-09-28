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
from enum import Enum

import fiatlight
from fiatlight.fiat_types import Error, Unspecified, UnspecifiedValue, JsonDict
from fiatlight.fiat_core import FunctionNode, FunctionNodeLink, AnyDataWithGui
from fiatlight.fiat_core.gui_node import GuiNode
from fiatlight.fiat_core.any_data_with_gui import GuiHeaderLineParams
from fiatlight.fiat_config import FiatColorType, get_fiat_config
from fiatlight.fiat_core.param_with_gui import ParamWithGui
from fiatlight.fiat_nodes.value_in_node_vs_focused import ExpandedFlagInNodeVsFocused, FlagsDictInNodeVsFocused
from imgui_bundle import (
    imgui,
    imgui_node_editor as ed,
    ImVec2,
    imgui_ctx,
    hello_imgui,
    imgui_node_editor_ctx as ed_ctx,
    imspinner,
    ImColor,
    imgui_md,
)
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx, fiat_osd
from fiatlight import fiat_widgets, fiat_togui, fiat_utils
from typing import Dict, List, Any
from dataclasses import dataclass
from fiatlight.fiat_utils.value_per_imgui_frame import ValuePerImGuiFrame


_CURRENT_FUNCTION_NODE_ID: ed.NodeId | None = None

_LAST_FOCUSED_FUNCTION_SCREENSHOT_RECT = ValuePerImGuiFrame[imgui.internal.ImRect]()


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

    # Fine tune function internals
    # (displayed if the user adds a *function variable* dictionary named fiat_tuning)
    _fiat_tuning_with_gui: Dict[str, AnyDataWithGui[Any]]

    # user settings:
    #   Flags that indicate whether the details of the inputs/outputs/internals are shown or not
    #   (those settings are saved in the user settings file)
    _inputs_expanded: ExpandedFlagInNodeVsFocused
    _outputs_expanded: ExpandedFlagInNodeVsFocused
    _doc_expanded: ExpandedFlagInNodeVsFocused
    fiat_tuning_expanded: ExpandedFlagInNodeVsFocused  # This is for the debug internals
    _internal_state_gui_expanded: ExpandedFlagInNodeVsFocused  # This is for the function's internal state gui

    # Backup of the expanded states when the user clicks on the minimize button
    # (two sets of flags: one for the node mode, one for the focused mode)
    _backup_expanded_states: FlagsDictInNodeVsFocused

    # id of the imgui frame_count where a change in the focused window happened
    _focused_window_change_frame_id: int = 0
    _focused_window_was_visible_at_exit: bool | None = None

    # ==================================================================================================================
    #                                            Constructor
    # ==================================================================================================================
    class _Constructor_Section:  # Dummy class to create a section in the IDE # noqa
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

        self._fiat_tuning_with_gui = {}

        self._inputs_expanded = ExpandedFlagInNodeVsFocused(True)
        self._outputs_expanded = ExpandedFlagInNodeVsFocused(True)
        self._doc_expanded = ExpandedFlagInNodeVsFocused(False)
        self.fiat_tuning_expanded = ExpandedFlagInNodeVsFocused(False)

        self._internal_state_gui_expanded = ExpandedFlagInNodeVsFocused(True)
        self._backup_expanded_states = FlagsDictInNodeVsFocused(None, None)

    class _Node_Info_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ==================================================================================================================
        #                                            Node info
        #                           (i.e. imgui-node-editor node id, size, etc.)
        # ==================================================================================================================

        """

        pass

    def node_id(self) -> ed.NodeId:
        return self._node_id

    def node_size(self) -> ImVec2:
        assert self._node_size is not None
        return self._node_size

    class _Utilities_Section:  # Dummy class to create a section in the IDE # noqa
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

    def _nb_outputs_with_custom_present(self) -> int:
        r = 0
        nb_outputs = self._function_node.function_with_gui.nb_outputs()
        for i in range(nb_outputs):
            if self._function_node.function_with_gui.output(i)._can_present_on_next_lines_if_expanded(
                is_expand_disabled=False
            ):
                r += 1
        return r

    def invoke(self) -> None:
        self._function_node.call_invoke_async_or_not()

    def __str__(self) -> str:
        return f"FunctionNodeGui({self._function_node.function_with_gui})"

    class _Draw_Node_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ==================================================================================================================
        #                                            Draw the node
        #         This is the heart of the class, with `draw_node` being the main function
        # ==================================================================================================================
        """

        pass

    def draw_node(self) -> bool:
        global _CURRENT_FUNCTION_NODE_ID
        inputs_changed: bool
        needs_refresh_for_heartbeat = self._heartbeat()
        with imgui_ctx.push_obj_id(self._function_node):
            try:
                id_node_or_focused = "node" if fiat_utils.is_rendering_in_node() else "focused"
                imgui.push_id(id_node_or_focused)
                if fiat_utils.is_rendering_in_node():
                    ed.begin_node(self._node_id)
                else:
                    imgui.begin_group()
                _CURRENT_FUNCTION_NODE_ID = self._node_id
                with imgui_ctx.begin_vertical("node_content"):
                    # Title
                    with imgui_ctx.begin_horizontal("Title"):
                        self._draw_title()
                    # Doc
                    self._draw_doc()
                    # Set minimum width
                    imgui.dummy(ImVec2(hello_imgui.em_size(get_fiat_config().style.node_minimum_width_em), 1))

                    # Inputs
                    inputs_changed = self._draw_function_inputs()
                    # Function internal state
                    internal_state_changed = self._draw_function_internal_state()

                    if inputs_changed or internal_state_changed or needs_refresh_for_heartbeat:
                        self._function_node.on_inputs_changed()

                    # Fiat tuning
                    self._draw_fiat_tuning()
                    # Exceptions, if any
                    self._draw_exception_message()
                    # Outputs
                    self._draw_function_outputs()
                if fiat_utils.is_rendering_in_node():
                    ed.end_node()
                else:
                    imgui.end_group()
                    function_rect = imgui.internal.ImRect(imgui.get_item_rect_min(), imgui.get_item_rect_max())
                    _LAST_FOCUSED_FUNCTION_SCREENSHOT_RECT.set(function_rect)
                imgui.pop_id()
            except Exception as e:
                function_with_gui = self._function_node.function_with_gui
                # Capture the callstack on your library's side first
                import traceback

                user_stack_trace = traceback.format_exc()
                msg = f"""
                User code stack trace:
                {user_stack_trace}

                Error while drawing node for Function:
                    Function Name={self._function_node.function_with_gui.function_name}
                    Function Label={function_with_gui.label}
                    FunctionWithGui Type={type(function_with_gui)}
            """
                raise Exception(msg) from e
            self._node_size = ed.get_node_size(self._node_id)
        return inputs_changed

    class _Draw_Title_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #  Draw title and header lines
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

    def _draw_title(self) -> None:
        fn_label = self._function_node.function_with_gui.label
        # Hide ## suffix
        fn_label = fn_label.split("##")[0]

        bold_font = imgui_md.get_font(imgui_md.MarkdownFontSpec(bold_=True))
        with imgui_ctx.push_font(bold_font.font):
            imgui.text("      " + fn_label)
        function_name = self._function_node.function_with_gui.function_name
        if function_name != fn_label:
            fiat_osd.set_widget_tooltip(f" (id: {function_name})")

        self._draw_doc_info_icon_on_title_line()
        self._draw_async_status_on_title_line()
        imgui.spring()
        self._draw_minimize_btn()
        self._focused_function_draw_button()

    def _draw_minimize_btn(self) -> None:
        """
        The minimize button enable to collapse / expand the different sections:
              _inputs_expanded, _outputs_expanded, _doc_expanded, fiat_tuning_expanded, _internal_state_gui_expanded
        Its behavior is as follows:
            if any expanded => collapse all and save state
            if all collapsed
                if any saved state => restore saved state | destroy saved state
                else => expand all
        """
        has_inputs = self._function_node.function_with_gui.nb_inputs() > 0
        has_outputs = self._function_node.function_with_gui.nb_outputs() > 0
        has_doc = self._function_node.function_with_gui.get_function_doc().user_doc is not None
        has_fiat_tuning = len(self._fiat_tuning_with_gui) > 0
        has_internal_state_gui = self._function_node.function_with_gui.internal_state_gui is not None
        any_expanded = (
            False
            or (self._inputs_expanded.current_value() and has_inputs)
            or (self._outputs_expanded.current_value() and has_outputs)
            or (self._doc_expanded.current_value() and has_doc)
            or (self.fiat_tuning_expanded.current_value() and has_fiat_tuning)
            or (self._internal_state_gui_expanded.current_value() and has_internal_state_gui)
        )

        class PossibleAction(Enum):
            None_ = 0
            CollapseAll = 1
            Expand = 2

        def display_btn() -> PossibleAction:
            result = PossibleAction.None_
            with fontawesome_6_ctx():
                if any_expanded:
                    clicked_minimize = imgui.button(icons_fontawesome_6.ICON_FA_WINDOW_MINIMIZE)
                    fiat_osd.set_widget_tooltip("Collapse all")
                    if clicked_minimize:
                        result = PossibleAction.CollapseAll
                else:
                    clicked_restore = imgui.button(icons_fontawesome_6.ICON_FA_WINDOW_MAXIMIZE)
                    fiat_osd.set_widget_tooltip("Expand")
                    if clicked_restore:
                        result = PossibleAction.Expand
                return result

        def handle_action(action: PossibleAction) -> None:
            if action == PossibleAction.None_:
                return
            elif action == PossibleAction.CollapseAll:
                self._backup_expanded_states.set_current_value(
                    {
                        "inputs": self._inputs_expanded.current_value(),
                        "outputs": self._outputs_expanded.current_value(),
                        "doc": self._doc_expanded.current_value(),
                        "fiat_tuning": self.fiat_tuning_expanded.current_value(),
                        "internal_state_gui": self._internal_state_gui_expanded.current_value(),
                    }
                )
                self._inputs_expanded.set_current_value(False)
                self._outputs_expanded.set_current_value(False)
                self._doc_expanded.set_current_value(False)
                self.fiat_tuning_expanded.set_current_value(False)
                self._internal_state_gui_expanded.set_current_value(False)
            elif action == PossibleAction.Expand:
                backup = self._backup_expanded_states.current_value()
                if backup is not None:
                    self._inputs_expanded.set_current_value(backup["inputs"])
                    self._outputs_expanded.set_current_value(backup["outputs"])
                    self._doc_expanded.set_current_value(backup["doc"])
                    self.fiat_tuning_expanded.set_current_value(backup["fiat_tuning"])
                    self._internal_state_gui_expanded.set_current_value(backup["internal_state_gui"])
                    self._backup_expanded_states.set_current_value(None)
                else:
                    if has_inputs:
                        self._inputs_expanded.set_current_value(True)
                    if has_outputs:
                        self._outputs_expanded.set_current_value(True)
                    if has_doc:
                        self._doc_expanded.set_current_value(True)
                    if has_fiat_tuning:
                        self.fiat_tuning_expanded.set_current_value(True)
                    if has_internal_state_gui:
                        self._internal_state_gui_expanded.set_current_value(True)

        action_ = display_btn()
        handle_action(action_)

    def _draw_async_status_on_title_line(self) -> None:
        if self._function_node.is_running_async():
            color_vec4 = get_fiat_config().style.color_as_vec4(FiatColorType.SpinnerAsync)
            color = ImColor(color_vec4)
            radius1 = imgui.get_font_size() / 3.5
            imgui.spring()

            def show_async_stop_button() -> None:
                fn_with_gui = self._function_node.function_with_gui
                if not fn_with_gui.invoke_async_stoppable:
                    return
                fn = fn_with_gui._f_impl
                assert fn is not None
                is_stopping = fiatlight.get_fiat_attribute(fn, "invoke_async_shall_stop", False)
                if is_stopping:
                    imgui.text("Stopping...")
                    if imgui.button("Cancel"):
                        fiatlight.set_fiat_attribute(fn, "invoke_async_shall_stop", False)
                else:
                    if imgui.button("Stop"):
                        fiatlight.set_fiat_attribute(fn, "invoke_async_shall_stop", True)

            show_async_stop_button()

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

    class _Draw_Inputs_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #       Draw inputs
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

    def _draw_function_inputs(self) -> bool:
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
        node_separator_params.expanded = self._inputs_expanded.current_value()
        # Separator text
        node_separator_params.text = "Params" if nb_inputs > 1 else "Param"
        if nb_unlinked_inputs > 0 and not self._inputs_expanded.current_value():
            node_separator_params.text += f" ({nb_unlinked_inputs} hidden)"
        # Separator collapse button
        node_separator_params.show_collapse_button = nb_inputs >= 1
        # Separator collapse all button
        node_separator_params.show_toggle_collapse_all_button = (
            nb_unlinked_inputs > 1
            and self._inputs_expanded.current_value()
            and self._function_node.function_with_gui._nb_collapsible_inputs() > 0
        )

        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)

        # Update the expanded state
        self._inputs_expanded.set_current_value(node_separator_output.expanded)

        # Update the inputs expanded state
        if node_separator_output.was_toggle_collapse_all_clicked:
            self._function_node.function_with_gui.toggle_expand_inputs()

        #
        # Draw the inputs
        #
        for param_name in self._function_node.function_with_gui.all_inputs_names():
            input_param = self._function_node.function_with_gui.param(param_name)
            if self._draw_one_input(input_param):
                changed = True

        if shall_disable_input:
            imgui.end_disabled()

        return changed

    def _draw_one_input(self, input_param: ParamWithGui[Any]) -> bool:
        with imgui_ctx.push_obj_id(input_param):
            input_name = input_param.name

            has_link = self._function_node.has_input_link(input_name)
            if not has_link and not self._inputs_expanded.current_value():
                return False

            can_edit = not has_link

            header_elements = self._input_param_header_elements(input_param)

            input_param.data_with_gui.label_color = get_fiat_config().style.color_as_vec4(
                header_elements.param_label_color
            )
            input_param.data_with_gui.status_tooltip = header_elements.param_label_tooltip

            header_params = GuiHeaderLineParams[Any](parent_name=self._function_node.function_with_gui.label)
            if fiat_utils.is_rendering_in_node():
                header_params.prefix_gui = lambda: self._draw_input_pin(header_elements)
            header_params.default_value_if_unspecified = input_param.default_value

            header_params.is_expand_disabled = not self._inputs_expanded.current_value()

            if can_edit:
                changed = input_param.data_with_gui.gui_edit_customizable(header_params)
                return changed
            else:
                input_param.data_with_gui.gui_present_customizable(header_params)
                return False

    class _Draw_Outputs_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #       Draw outputs
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

    def _draw_function_outputs(self) -> None:
        nb_outputs = self._function_node.function_with_gui.nb_outputs()
        nb_unlinked_outputs = self._function_node.nb_unlinked_outputs()

        if nb_outputs == 0 and not self._function_node.function_with_gui.invoke_manually:
            return

        #
        # Instantiate the node separator parameters
        #
        node_separator_params = fiat_widgets.NodeSeparatorParams()
        node_separator_params.parent_node = self._node_id
        # expanded state
        node_separator_params.expanded = self._outputs_expanded.current_value()
        # Separator text
        node_separator_params.text = "Outputs" if nb_outputs > 1 else "Output"
        if nb_unlinked_outputs > 0 and not self._outputs_expanded.current_value():
            node_separator_params.text += f" ({nb_unlinked_outputs} hidden)"
        # show collapse button
        node_separator_params.show_collapse_button = nb_outputs > 0
        # show collapse all button
        node_separator_params.show_toggle_collapse_all_button = (
            self._outputs_expanded.current_value()
            and self._nb_outputs_with_custom_present() > 0
            and self._function_node.function_with_gui._nb_collapsible_outputs() > 0
        )

        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)

        # Update the expanded state
        self._outputs_expanded.set_current_value(node_separator_output.expanded)
        # If the collapse all button was clicked, we update the state of all outputs
        if node_separator_output.was_toggle_collapse_all_clicked:
            self._function_node.function_with_gui.toggle_expand_outputs()

        # Invoke options
        self._draw_invoke_options()

        # Outputs
        for idx_output in range(self._function_node.function_with_gui.nb_outputs()):
            has_link = len(self._function_node.output_links_for_idx(idx_output)) > 0
            if not has_link and not self._outputs_expanded.current_value():
                continue
            with imgui_ctx.begin_group():
                self._draw_one_output(idx_output)

    def _draw_one_output(self, idx_output: int) -> None:
        output_param = self._function_node.function_with_gui.output(idx_output)

        bof_header_elements = self._output_header_elements(idx_output)

        output_param.label_color = get_fiat_config().style.color_as_vec4(bof_header_elements.value_color)
        output_param.status_tooltip = bof_header_elements.value_tooltip

        header_params = GuiHeaderLineParams[Any](parent_name=self._function_node.function_with_gui.label)
        if fiat_utils.is_rendering_in_node():
            header_params.suffix_gui = lambda: self._draw_output_pin(bof_header_elements, idx_output)

        header_params.is_expand_disabled = not self._outputs_expanded.current_value()

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
                    if imgui.button("Call manually"):
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

    class _Draw_Internals_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #      Draw function Internal State and fiat_tuning (debug help)
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

    def _draw_function_internal_state(self) -> bool:
        fn_with_gui = self._function_node.function_with_gui
        internal_state_fn = fn_with_gui.internal_state_gui
        if internal_state_fn is None:
            return False

        can_collapse = True
        expanded = self._internal_state_gui_expanded.current_value()

        is_gui_only_node = self._function_node.function_with_gui.invoke_is_gui_only

        #
        # Draw the separator
        #
        if not is_gui_only_node:
            node_separator_params = fiat_widgets.NodeSeparatorParams()
            node_separator_params.parent_node = self._node_id
            # expanded state
            node_separator_params.expanded = expanded
            # Separator text
            if isinstance(fn_with_gui, GuiNode):
                node_separator_params.text = " "
            else:
                node_separator_params.text = "Function internal state"
            # Separator collapse button
            node_separator_params.show_collapse_button = can_collapse
            # Separator collapse all button
            node_separator_params.show_toggle_collapse_all_button = False

            # Draw the separator
            node_separator_output = fiat_widgets.node_separator(node_separator_params)
            # Update the expanded state
            self._internal_state_gui_expanded.set_current_value(node_separator_output.expanded)

        #
        # Invoke the internal state gui
        #
        changed = False

        if not is_gui_only_node:
            detached_internal_state_fn = fiat_osd.DetachedWindowParams(
                unique_id="internal_state" + str(id(internal_state_fn)),
                window_name=f"{self._function_node.function_with_gui.label} Internal GUI",
                gui_function=internal_state_fn,
            )
            fiat_osd.show_bool_detached_window_button(detached_internal_state_fn)

            # If the user edits the internal gui in a detached window
            if fiat_osd.get_detached_window_bool_return(detached_internal_state_fn):
                changed = True

        if self._internal_state_gui_expanded.current_value():
            changed = internal_state_fn()

        return changed

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
        node_separator_params.expanded = self.fiat_tuning_expanded.current_value()
        node_separator_params.text = "Fiat Tuning"
        node_separator_params.show_collapse_button = True
        node_separator_params.show_toggle_collapse_all_button = self.fiat_tuning_expanded.current_value()
        if not self.fiat_tuning_expanded.current_value():
            node_separator_params.text += f" ({len(fn_fiat_tuning)} hidden)"

        # Draw the separator
        node_separator_output = fiat_widgets.node_separator(node_separator_params)

        # Update the expanded state
        self.fiat_tuning_expanded.set_current_value(node_separator_output.expanded)

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

        if not self.fiat_tuning_expanded.current_value():
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

    class _Draw_Misc_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #      Draw misc elements
        # ------------------------------------------------------------------------------------------------------------------
        """

        pass

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
            get_fiat_config().style.str_truncation.exceptions,
            color=get_fiat_config().style.color_as_vec4(FiatColorType.ExceptionError),
        )

        # Raise the exception so that the user can debug it
        with fontawesome_6_ctx():

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

            detached_window_params = fiat_osd.DetachedWindowParams(
                unique_id="raise_exception" + str(id(self)),
                window_name="Confirm Raise exception",
                gui_function=confirmation_gui,
                button_label=icons_fontawesome_6.ICON_FA_BOMB + " Debug this exception",
                window_flags=imgui.WindowFlags_.always_auto_resize.value,
            )
            fiat_osd.show_void_detached_window_button(detached_window_params)

    def _draw_doc_info_icon_on_title_line(self) -> None:
        fn_with_gui = self._function_node.function_with_gui
        doc = fn_with_gui.get_function_doc()
        if doc.user_doc is None:
            return
        with fontawesome_6_ctx():
            if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_INFO):
                self._doc_expanded.set_current_value(not self._doc_expanded.current_value())
            tooltip = "Show documentation" if not self._doc_expanded.current_value() else "Hide documentation"
            fiat_osd.set_widget_tooltip(tooltip)

    def _draw_doc(self) -> None:
        fn_with_gui = self._function_node.function_with_gui

        doc = fn_with_gui.get_function_doc()

        if doc.user_doc is None or not self._doc_expanded.current_value():
            return

        def render_user_doc() -> None:
            assert doc.user_doc is not None
            if doc.is_user_doc_markdown:
                imgui_md.render_unindented(doc.user_doc)
            else:
                imgui.text_wrapped(doc.user_doc)

        render_user_doc()

    class _FocusedFunction:  # Dummy class to create a section in the IDE # noqa
        """
        # ==================================================================================================================
        # Focused Function Section: function nodes can also be displayed in a separate window
        # known as focused function.
        # ==================================================================================================================
        """

    _focused_function_visible: bool = False

    def _focused_function_draw_button(self) -> None:
        if not fiat_utils.is_rendering_in_node():
            return
        if not self._focused_function_visible:
            with fontawesome_6_ctx():
                clicked = imgui.button(icons_fontawesome_6.ICON_FA_UP_RIGHT_FROM_SQUARE, ImVec2(0, 0))
                fiat_osd.set_widget_tooltip("Focus on function in a separate window")
                if clicked:
                    self._focused_function_visible = True

    def _focused_function_label(self) -> str:
        function_name = self.get_function_node().function_with_gui.function_name
        function_label = self.get_function_node().function_with_gui.label
        label = function_label
        if label != function_name:
            label += " (" + function_name + ")"
        return label + "##FocusedFunctionsInTabs"

    def focused_function_draw_window(self) -> None:
        if not self._focused_function_visible:
            return

        window_flags = 0 | imgui.WindowFlags_.always_auto_resize.value
        shall_draw, still_visible = imgui.begin(
            self._focused_function_label(), self._focused_function_visible, window_flags
        )
        if shall_draw:
            changed = self.draw_node()
            if changed:
                self._focused_window_change_frame_id = imgui.get_frame_count()

        imgui.end()
        assert still_visible is not None
        self._focused_function_visible = still_visible

    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
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
            "_inputs_expanded": self._inputs_expanded.save_to_dict(),
            "_outputs_expanded": self._outputs_expanded.save_to_dict(),
            "_doc_expanded": self._doc_expanded.save_to_dict(),
            "fiat_tuning_expanded": self.fiat_tuning_expanded.save_to_dict(),
            "_internal_state_gui_expanded": self._internal_state_gui_expanded.save_to_dict(),
            "_function_node": self._function_node.save_gui_options_to_json(),
            "_backup_expanded_states": self._backup_expanded_states.save_to_dict(),
            "_focused_function_visible": self._focused_function_visible,
            # "_fiat_tuning_with_gui": fiat_tuning_options,
        }
        return r

    def load_gui_options_from_json(self, json_data: JsonDict) -> None:
        self._inputs_expanded = ExpandedFlagInNodeVsFocused.load_from_dict(json_data["_inputs_expanded"])
        self._outputs_expanded = ExpandedFlagInNodeVsFocused.load_from_dict(json_data["_outputs_expanded"])
        self._doc_expanded = ExpandedFlagInNodeVsFocused.load_from_dict(json_data["_doc_expanded"])
        self.fiat_tuning_expanded = ExpandedFlagInNodeVsFocused.load_from_dict(json_data["fiat_tuning_expanded"])
        self._internal_state_gui_expanded = ExpandedFlagInNodeVsFocused.load_from_dict(
            json_data["_internal_state_gui_expanded"]
        )
        if "_backup_expanded_states" in json_data:
            self._backup_expanded_states = FlagsDictInNodeVsFocused.load_from_dict(json_data["_backup_expanded_states"])

        if "_focused_function_visible" in json_data:
            self._focused_function_visible = json_data["_focused_function_visible"]

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
        ed.link(
            self.link_id,
            self.start_id,
            self.end_id,
            color=get_fiat_config().style.color_as_vec4(FiatColorType.LinkFunctions),
        )


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
