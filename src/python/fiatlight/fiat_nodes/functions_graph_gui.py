from __future__ import annotations
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_core.function_with_gui import FunctionWithGuiFactoryFromName
from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui, FunctionNodeLinkGui
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_node_editor as ed, hello_imgui, ImVec2, imgui_ctx
from typing import List, Dict, Tuple


KK_STATIC_FunctionsGraphGui: FunctionsGraphGui | None = None


class FunctionsGraphGui:
    functions_graph: FunctionsGraph

    function_nodes_gui: List[FunctionNodeGui]
    functions_links_gui: List[FunctionNodeLinkGui]

    shall_layout_graph: bool = False
    can_edit_graph: bool = False

    _idx_frame: int = 0
    _function_no_node_editor_rect: imgui.internal.ImRect | None = None
    _use_node_editor_if_one_function: bool = False

    # ======================================================================================================================
    # Constructor
    # ======================================================================================================================
    def __init__(self, functions_graph: FunctionsGraph, use_node_editor_if_one_function: bool) -> None:
        self._use_node_editor_if_one_function = use_node_editor_if_one_function
        self.functions_graph = functions_graph
        self._create_function_nodes_and_links_gui()
        global KK_STATIC_FunctionsGraphGui
        KK_STATIC_FunctionsGraphGui = self

    def _create_function_nodes_and_links_gui(self) -> None:
        self.function_nodes_gui = []
        for f in self.functions_graph.functions_nodes:
            self.function_nodes_gui.append(FunctionNodeGui(f))

        self.functions_links_gui = []
        for link in self.functions_graph.functions_nodes_links:
            link_gui = FunctionNodeLinkGui(link, self.function_nodes_gui)
            self.functions_links_gui.append(link_gui)

    # ======================================================================================================================
    # Drawing
    # ======================================================================================================================
    class _Drawing_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def shall_use_node_editor(self) -> bool:
        if len(self.function_nodes_gui) > 1:
            return True
        return self._use_node_editor_if_one_function

    @staticmethod
    def _handle_global_zoom_if_no_node_editor() -> None:
        # imgui.text("(?)")
        # fiat_osd.set_widget_tooltip("Ctrl+Alt+Wheel to zoom")
        ctrl_down = imgui.is_key_down(imgui.Key.left_ctrl) or imgui.is_key_down(imgui.Key.right_ctrl)
        alt_down = imgui.is_key_down(imgui.Key.left_alt) or imgui.is_key_down(imgui.Key.right_alt)
        mod_ok = ctrl_down and alt_down
        if not mod_ok:
            return

        wheel_amount = imgui.get_io().mouse_wheel
        if wheel_amount == 0:
            return
        k = 1.0 + wheel_amount / 20
        imgui.get_io().font_global_scale *= k

    def draw(self) -> bool:
        from fiatlight.fiat_utils import fiat_node_semaphore

        shall_use_node_editor = self.shall_use_node_editor()

        def draw_nodes() -> bool:
            changed = False
            for fn in self.function_nodes_gui:
                imgui.push_id(str(id(fn)))
                unique_fn_name = self.functions_graph.function_node_unique_name(fn._function_node)
                if fn.draw_node(unique_fn_name):
                    changed = True
                imgui.pop_id()
            return changed

        def draw_links() -> None:
            for link in self.functions_links_gui:
                link.draw()

        if not shall_use_node_editor:
            self._handle_global_zoom_if_no_node_editor()

        self._layout_graph_if_required()
        nodes_changed = False
        with imgui_ctx.push_obj_id(self):
            if shall_use_node_editor:
                ed.begin("FunctionsGraphGui")
                fiat_node_semaphore._IS_RENDERING_IN_NODE = True
            else:
                imgui.begin_group()
            if draw_nodes():
                nodes_changed = True
            draw_links()
            if self.can_edit_graph:
                self._handle_graph_edition()
            if shall_use_node_editor:
                ed.end()
                fiat_node_semaphore._IS_RENDERING_IN_NODE = False
            else:
                imgui.end_group()
                self._function_no_node_editor_rect = imgui.internal.ImRect(
                    imgui.get_item_rect_min(), imgui.get_item_rect_max()
                )
        self._idx_frame += 1
        return nodes_changed

    def _handle_graph_edition(self) -> None:
        #
        # Handle creation action, returns true if editor want to create new object (node or link)
        #
        if ed.begin_create():
            input_pin_id = ed.PinId()
            output_pin_id = ed.PinId()

            # QueryNewLink returns true if editor want to create new link between pins.
            if ed.query_new_link(input_pin_id, output_pin_id):
                if input_pin_id and output_pin_id and input_pin_id != output_pin_id:
                    can_add_link, fail_reason = self._can_add_link(input_pin_id, output_pin_id)
                    if not can_add_link:
                        ed.reject_new_item()
                        fiat_osd.set_tooltip(fail_reason)
                    else:
                        if ed.accept_new_item():
                            self._try_add_link(input_pin_id, output_pin_id)
            ed.end_create()

        # Handle deletion action
        if ed.begin_delete():
            link_id = ed.LinkId()
            # Handle link deletion
            while ed.query_deleted_link(link_id):
                if ed.accept_deleted_item():
                    self._remove_link(link_id)

            # Handle node deletion
            node_id = ed.NodeId()
            while ed.query_deleted_node(node_id):
                if ed.accept_deleted_item():
                    self._remove_function_node(node_id)

            ed.end_delete()

        # Handle hovered link
        hovered_link = ed.get_hovered_link()
        if hovered_link.id() > 0:
            fiat_osd.set_tooltip(f"Link hovered: {hovered_link.id()}")

        # Handle link context menu
        link_context_menu_id = ed.LinkId()
        if ed.show_link_context_menu(link_context_menu_id):

            def show_link_context_menu() -> None:
                imgui.text(f"Link context menu: {link_context_menu_id}")
                if imgui.menu_item_simple("Delete pin"):
                    self._remove_link(link_context_menu_id)

            fiat_osd.set_popup_gui(show_link_context_menu)

        # Handle node context menu
        node_context_menu_id = ed.NodeId()
        if ed.show_node_context_menu(node_context_menu_id):

            def show_node_context_menu() -> None:
                imgui.text(f"Node context menu: {node_context_menu_id}")
                if imgui.menu_item_simple("Delete node"):
                    self._remove_function_node(node_context_menu_id)

            fiat_osd.set_popup_gui(show_node_context_menu)

    # ======================================================================================================================
    # Graph manipulation
    # ======================================================================================================================
    class _GraphManipulation_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def add_function_with_gui(self, function: FunctionWithGui) -> None:
        function_node = self.functions_graph.add_function(function)
        function_node_gui = FunctionNodeGui(function_node)
        self.function_nodes_gui.append(function_node_gui)

    def _can_add_link(self, input_pin_id: ed.PinId, output_pin_id: ed.PinId) -> Tuple[bool, str]:
        # 1. Look for the function node GUIs that correspond to the input and output pins
        fn_input, dst_param_name = self._function_node_gui_from_input_pin_id(input_pin_id)
        fn_output, src_output_idx = self._function_node_gui_from_output_pin_id(output_pin_id)
        if fn_input is None or fn_output is None:
            fn_input, dst_param_name = self._function_node_gui_from_input_pin_id(output_pin_id)
            fn_output, src_output_idx = self._function_node_gui_from_output_pin_id(input_pin_id)
        if fn_input is None or fn_output is None:
            return (
                False,
                "Can not add link! Please link an output pin (Right) to an input pin (Left) of another function",
            )

        ok, failure_reason = self.functions_graph._can_add_link(
            fn_output.get_function_node(), fn_input.get_function_node(), dst_param_name, src_output_idx
        )
        if not ok:
            return False, failure_reason
        else:
            return True, ""

    def _try_add_link(self, input_pin_id: ed.PinId, output_pin_id: ed.PinId) -> bool:
        # 1. Look for the function node GUIs that correspond to the input and output pins
        fn_input, dst_param_name = self._function_node_gui_from_input_pin_id(input_pin_id)
        fn_output, src_output_idx = self._function_node_gui_from_output_pin_id(output_pin_id)
        if fn_input is None or fn_output is None:
            fn_input, dst_param_name = self._function_node_gui_from_input_pin_id(output_pin_id)
            fn_output, src_output_idx = self._function_node_gui_from_output_pin_id(input_pin_id)
        if fn_input is None or fn_output is None:
            return False

        ok, _failure_reason = self.functions_graph._can_add_link(
            fn_output.get_function_node(), fn_input.get_function_node(), dst_param_name, src_output_idx
        )
        if not ok:
            return False

        # 2. Create and add the links to the lists
        # We need to add
        # - a link to self.functions_graph.functions_nodes_links
        # - and a link to self.functions_links_gui
        function_node_link = self.functions_graph._add_link_from_function_nodes(
            fn_output.get_function_node(), fn_input.get_function_node(), dst_param_name, src_output_idx
        )
        function_node_link_gui = FunctionNodeLinkGui(function_node_link, self.function_nodes_gui)
        self.functions_links_gui.append(function_node_link_gui)

        return True

    def _remove_link(self, link_id: ed.LinkId) -> None:
        # 1. Find the link in the list of links
        link_gui = next(link for link in self.functions_links_gui if link.link_id == link_id)
        link = link_gui.function_node_link

        # 2. Remove the link from the lists
        self.functions_graph._remove_link(link)
        self.functions_links_gui.remove(link_gui)

    def _remove_function_node(self, node_id: ed.NodeId) -> None:
        # 1. Find the node in the list of nodes
        fn_gui = self._function_node_gui_from_id(node_id)
        fn = fn_gui.get_function_node()

        # 2. Remove the node from the lists
        self.functions_graph._remove_function_node(fn)
        self.function_nodes_gui.remove(fn_gui)

        # 3. Remove all links that are connected to this node
        links_to_remove = []
        for link_gui in self.functions_links_gui:
            if (
                link_gui.function_node_link.src_function_node == fn
                or link_gui.function_node_link.dst_function_node == fn
            ):
                links_to_remove.append(link_gui)
        for link_gui in links_to_remove:
            self.functions_links_gui.remove(link_gui)

    # ======================================================================================================================
    # Graph layout
    # ======================================================================================================================
    def _layout_graph_if_required(self) -> None:
        def are_all_nodes_on_zero() -> bool:
            # the node sizes are not set yet in the first frame
            # we need to wait until we know them
            if self._idx_frame == 0:
                return False

            for node in self.function_nodes_gui:
                pos = ed.get_node_position(node.node_id())
                if pos.x != 0 or pos.y != 0:
                    return False
            return True

        if self.shall_layout_graph or are_all_nodes_on_zero():
            self.shall_layout_graph = False
            width_between_nodes = hello_imgui.em_size(4)
            height_between_nodes = hello_imgui.em_size(4)
            current_row_height = 0.0
            w = imgui.get_window_width()
            current_position = ImVec2(0, 0)

            for i, fn in enumerate(self.function_nodes_gui):
                ed.set_node_position(fn.node_id(), current_position)
                node_size = ed.get_node_size(fn.node_id())
                current_position.x += node_size.x + width_between_nodes
                current_row_height = max(current_row_height, node_size.y)
                if current_position.x + node_size.x > w:
                    current_position.x = 0
                    current_position.y += current_row_height + height_between_nodes
                    current_row_height = 0

    def _get_node_screenshot_boundings(self) -> imgui.internal.ImRect:
        if not self.shall_use_node_editor():
            assert self._function_no_node_editor_rect is not None
            r = self._function_no_node_editor_rect
            main_viewport_pos = imgui.get_main_viewport().pos
            fbs = imgui.get_io().display_framebuffer_scale
            r.min -= main_viewport_pos  # type: ignore # noqa
            r.max -= main_viewport_pos  # type: ignore
            r.min = r.min * fbs  # type: ignore
            r.max = r.max * fbs  # type: ignore
            return r

        all_nodes_boundings = []
        for fn in self.function_nodes_gui:
            node_id = fn.node_id()
            # position and size are in canvas coordinates
            node_tl = ed.get_node_position(node_id)
            node_br = node_tl + ed.get_node_size(node_id)  # type: ignore
            # convert to screen coordinates (i.e coordinates on the computer screen)
            node_tl = ed.canvas_to_screen(node_tl)
            node_br = ed.canvas_to_screen(node_br)
            # convert to viewport coordinates (i.e. from the top left corner of the app window)
            main_viewport_pos = imgui.get_main_viewport().pos
            node_tl -= main_viewport_pos  # type: ignore # noqa
            node_br -= main_viewport_pos
            # take into account the display frame buffer scale
            fbs = imgui.get_io().display_framebuffer_scale
            node_tl = node_tl * fbs  # type: ignore
            node_br = node_br * fbs
            # Add some margin
            margin = 3
            node_tl -= ImVec2(margin, margin)  # type: ignore
            node_br += ImVec2(margin, margin)
            # phew, done...

            all_nodes_boundings.append(imgui.internal.ImRect(node_tl, node_br))

        big = 1_000_000
        tl = ImVec2(big, big)
        br = ImVec2(-big, -big)
        for node_boundings in all_nodes_boundings:
            tl.x = min(tl.x, node_boundings.min.x)
            tl.y = min(tl.y, node_boundings.min.y)
            br.x = max(br.x, node_boundings.max.x)
            br.y = max(br.y, node_boundings.max.y)

        r = imgui.internal.ImRect(tl, br)
        if r.get_width() <= 0 or r.get_height() <= 0:
            raise ValueError("Invalid screenshot boundings: please make sure the nodes are fully visible")
        return r

    # ======================================================================================================================
    # Utilities
    # ======================================================================================================================
    class _Utilities_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def function_node_unique_name(self, function_node_gui: FunctionNodeGui) -> str:
        return self.functions_graph.function_node_unique_name(function_node_gui._function_node)  # noqa

    def function_node_with_unique_name(self, function_name: str) -> FunctionNodeGui:
        return next(fn for fn in self.function_nodes_gui if self.function_node_unique_name(fn) == function_name)

    def all_function_nodes_with_unique_names(self) -> Dict[str, FunctionNodeGui]:
        return {self.function_node_unique_name(fn): fn for fn in self.function_nodes_gui}

    def _function_node_gui_from_input_pin_id(self, pin_id: ed.PinId) -> Tuple[FunctionNodeGui | None, str]:
        matching_nodes = []
        for fn in self.function_nodes_gui:
            param_name = fn.input_pin_to_param_name(pin_id)
            if param_name is not None:
                matching_nodes.append((fn, param_name))
        if len(matching_nodes) == 0:
            return None, ""
        assert len(matching_nodes) == 1
        return matching_nodes[0]

    def _function_node_gui_from_output_pin_id(self, pin_id: ed.PinId) -> Tuple[FunctionNodeGui | None, int]:
        matching_nodes = []
        for fn in self.function_nodes_gui:
            output_idx = fn.output_pin_to_output_idx(pin_id)
            if output_idx is not None:
                matching_nodes.append((fn, output_idx))
        if len(matching_nodes) == 0:
            return None, -1
        assert len(matching_nodes) == 1
        return matching_nodes[0]

    def _function_node_gui_from_id(self, node_id: ed.NodeId) -> FunctionNodeGui:
        matching_nodes = [fn for fn in self.function_nodes_gui if fn.node_id() == node_id]
        if len(matching_nodes) == 0:
            raise ValueError(f"Node with id {node_id} not found")
        assert len(matching_nodes) == 1
        return matching_nodes[0]

    def invoke_all_functions(self, also_invoke_manual_function: bool) -> None:
        """Invoke all the functions of the graph"""

        # We need to do this in two steps:
        # 1. Mark all functions as dirty (so that the call to invoke_function will actually call the function)
        for fn in self.functions_graph.functions_nodes:
            fn.function_with_gui._dirty = True

        # 2. Invoke all the functions
        # This is done in a separate loop because the functions may depend on each other,
        # and a call to fn.invoke_function() may trigger a call to other functions
        # (and mark them as not dirty anymore as a side effect)
        for fn_node_gui in self.function_nodes_gui:
            invoke_manually = fn_node_gui.get_function_node().function_with_gui.invoke_manually
            shall_invoke = not invoke_manually or also_invoke_manual_function
            if fn_node_gui.get_function_node().function_with_gui.is_dirty() and shall_invoke:
                fn_node_gui.invoke()

    def on_exit(self) -> None:
        for fn in self.functions_graph.functions_nodes:
            fn.function_with_gui.on_exit()

    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ======================================================================================================================
        # Serialization
        # ======================================================================================================================
        """

        pass

    def save_user_inputs_to_json(self) -> JsonDict:
        return self.functions_graph.save_user_inputs_to_json()

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        self.functions_graph.load_user_inputs_from_json(json_data)

    def save_gui_options_to_json(self) -> JsonDict:
        function_gui_settings_dict = {}
        for name, fn_node_with_gui in self.all_function_nodes_with_unique_names().items():
            function_gui_settings_dict[name] = {
                "function_node_with_gui": fn_node_with_gui.save_gui_options_to_json(),
                "function_node": fn_node_with_gui.get_function_node().save_gui_options_to_json(),
            }
        return function_gui_settings_dict

    def load_gui_options_from_json(self, json_dict: JsonDict) -> None:
        for name, fn_node_with_gui in self.all_function_nodes_with_unique_names().items():
            if name in json_dict:
                json_data = json_dict[name]
                fn_node_with_gui.load_gui_options_from_json(json_data["function_node_with_gui"])
                fn_node_with_gui.get_function_node().load_gui_options_from_json(json_data["function_node"])

    def save_graph_composition_to_json(self) -> JsonDict:
        return self.functions_graph.save_graph_composition_to_json()

    def load_graph_composition_from_json(
        self, json_data: JsonDict, function_factory: FunctionWithGuiFactoryFromName
    ) -> None:
        self.functions_graph.load_graph_composition_from_json(json_data, function_factory)
        self._create_function_nodes_and_links_gui()
