from __future__ import annotations

import logging
from dataclasses import dataclass

from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_types.type_compat import is_link_compatible
from fiatlight.fiat_types.typename_utils import TypeLike
from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_core.function_node import FunctionNode
from fiatlight.fiat_core.function_with_gui import FunctionWithGuiFactoryFromName
from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui, FunctionNodeLinkGui
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_node_editor as ed, hello_imgui, ImVec2, imgui_ctx
from typing import Callable, List, Dict, Literal, Optional, Tuple


PinKind = Literal["input", "output"]
# Callback contract for the shared palette popup (right-click on canvas, or
# drag-from-pin). Two callbacks together so fiat_nodes does not need to know
# the FunctionPalette / PaletteFilter types.
#
# - `on_open_palette_popup(compat)` is called once on the frame the popup
#   opens; the implementation resets its filter state (and sets compatibility
#   if `compat` is not None).
# - `on_render_palette_popup_body(on_pick)` is called every frame the popup
#   is open; the implementation draws the palette body (search/tags/list) and
#   calls `on_pick(new_function_with_gui)` when the user picks an entry.
PaletteCompat = Tuple[TypeLike, PinKind]
OpenPalettePopupFn = Callable[[Optional[PaletteCompat]], None]
RenderPalettePopupBodyFn = Callable[[Callable[[FunctionWithGui], None]], None]


@dataclass(frozen=True)
class _PendingDragSpawn:
    """Captures a wire drop on empty canvas while the palette popup is open."""

    pin_id: ed.PinId
    pin_kind: PinKind
    pin_type: TypeLike
    screen_pos: ImVec2


class FunctionsGraphGui:
    # Palette popup geometry (em units, scaled by hello_imgui.em_size).
    _PALETTE_POPUP_WIDTH_EM = 40
    _PALETTE_POPUP_MAX_HEIGHT_EM = 35
    _PALETTE_POPUP_ID = "##palette_popup"

    functions_graph: FunctionsGraph

    function_nodes_gui: List[FunctionNodeGui]
    functions_links_gui: List[FunctionNodeLinkGui]

    shall_layout_graph: bool = False
    can_edit_graph: bool = False

    # Wired by FiatGui to the FunctionPalette. Both must be set for the
    # right-click and drag-from-pin popups to appear; if either is None, the
    # graph editor falls back to its old (popup-less) behavior.
    on_open_palette_popup: OpenPalettePopupFn | None = None
    on_render_palette_popup_body: RenderPalettePopupBodyFn | None = None

    _idx_render_graph: int = 0
    _idx_last_frame_render: int = 0
    # State for the shared palette popup (right-click on canvas OR drag-from-pin).
    _pending_drag_spawn: _PendingDragSpawn | None = None
    _bg_popup_screen_pos: ImVec2 | None = None  # set when right-click opens the popup
    _palette_popup_just_requested: bool = False  # True only on the frame open_popup is needed
    # When a node is spawned from a popup, we need to set its position inside
    # an ed.begin/end block — defer to the next frame.
    _pending_node_position: Tuple[ed.NodeId, ImVec2] | None = None

    # ======================================================================================================================
    # Constructor
    # ======================================================================================================================
    def __init__(self, functions_graph: FunctionsGraph) -> None:
        self.functions_graph = functions_graph
        self._create_function_nodes_and_links_gui()

    def _create_function_nodes_and_links_gui(self) -> None:
        self.function_nodes_gui = []
        for f in self.functions_graph.functions_nodes:
            fn_node_gui = FunctionNodeGui(f)
            self.function_nodes_gui.append(fn_node_gui)

        self.functions_links_gui = []
        for link in self.functions_graph.functions_nodes_links:
            link_gui = FunctionNodeLinkGui(link, self.function_nodes_gui)
            self.functions_links_gui.append(link_gui)

    # ======================================================================================================================
    # Drawing
    # ======================================================================================================================
    class _Drawing_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def draw(self) -> bool:
        self._idx_last_frame_render = imgui.get_frame_count()
        from fiatlight.fiat_utils import fiat_node_semaphore

        def draw_nodes() -> bool:
            changed = False
            for fn in self.function_nodes_gui:
                imgui.push_id(str(id(fn)))
                if fn.draw_node():
                    changed = True
                imgui.pop_id()
            return changed

        def draw_links() -> None:
            for link in self.functions_links_gui:
                link.draw()

        self._layout_graph_if_required()
        nodes_changed = False
        with imgui_ctx.push_obj_id(self):
            fiat_node_semaphore._IS_RENDERING_IN_NODE = True
            ed.begin("FunctionsGraphGui")
            self._apply_pending_node_position()
            if draw_nodes():
                nodes_changed = True
            draw_links()
            if self.can_edit_graph:
                self._handle_graph_edition()
            ed.end()
            fiat_node_semaphore._IS_RENDERING_IN_NODE = False
            if self.can_edit_graph:
                if self._draw_palette_popup():
                    nodes_changed = True
        self._idx_render_graph += 1
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

            # QueryNewNode returns true if the user dropped a wire on empty
            # canvas. We capture the pin and open a popup of compatible
            # functions on the next frame.
            new_node_pin_id = ed.PinId()
            if ed.query_new_node(new_node_pin_id):
                if new_node_pin_id and self._palette_popup_available():
                    if ed.accept_new_item():
                        self._begin_drag_spawn(new_node_pin_id)
            ed.end_create()

        # Right-click on empty canvas → palette popup (no compatibility filter).
        if self._palette_popup_available():
            if ed.show_background_context_menu():
                self._begin_background_palette_popup()

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
            if self._idx_render_graph == 0:
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

    def _get_last_focused_function_boundings(self) -> imgui.internal.ImRect:
        # shot_rect could be a rectangle from the focused function
        from fiatlight.fiat_nodes.function_node_gui import _LAST_FOCUSED_FUNCTION_SCREENSHOT_RECT

        shot_rect = _LAST_FOCUSED_FUNCTION_SCREENSHOT_RECT.get()
        if shot_rect is None:
            logging.warning("No focused function found, taking a screenshot of the whole window")
            shot_rect = imgui.internal.ImRect(
                imgui.get_main_viewport().pos,
                imgui.get_main_viewport().pos + imgui.get_main_viewport().size,  # noqa
            )

        r = shot_rect
        fbs = imgui.get_io().display_framebuffer_scale
        main_viewport_pos = imgui.get_main_viewport().pos
        r.min -= main_viewport_pos  # noqa
        r.max -= main_viewport_pos
        r.min = r.min * fbs
        r.max = r.max * fbs
        return r

    def _get_node_screenshot_boundings(self) -> imgui.internal.ImRect:
        if self._idx_last_frame_render != imgui.get_frame_count():
            # This might happen if the graph was not rendered in the current frame
            # (i.e. we switched to another tab)
            return self._get_last_focused_function_boundings()

        all_nodes_boundings = []
        for fn in self.function_nodes_gui:
            node_id = fn.node_id()
            # position and size are in canvas coordinates
            node_tl = ed.get_node_position(node_id)
            node_br = node_tl + ed.get_node_size(node_id)
            # convert to screen coordinates (i.e coordinates on the computer screen)
            node_tl = ed.canvas_to_screen(node_tl)
            node_br = ed.canvas_to_screen(node_br)
            # convert to viewport coordinates (i.e. from the top left corner of the app window)
            main_viewport_pos = imgui.get_main_viewport().pos
            node_tl -= main_viewport_pos
            node_br -= main_viewport_pos
            # take into account the display frame buffer scale
            fbs = imgui.get_io().display_framebuffer_scale
            node_tl = node_tl * fbs
            node_br = node_br * fbs
            # Add some margin
            margin = 3
            node_tl -= ImVec2(margin, margin)
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

    def function_name(self, function_node_gui: FunctionNodeGui) -> str:
        return function_node_gui.get_function_node().function_with_gui.function_name

    def function_node_name(self, function_name: str) -> FunctionNodeGui:
        return next(fn for fn in self.function_nodes_gui if self.function_name(fn) == function_name)

    def _dict_function_nodes(self) -> Dict[str, FunctionNodeGui]:
        return {self.function_name(fn): fn for fn in self.function_nodes_gui}

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

    # ------------------------------------------------------------------
    # Shared palette popup (right-click on canvas, or drag-from-pin)
    # ------------------------------------------------------------------
    def _palette_popup_available(self) -> bool:
        return self.on_open_palette_popup is not None and self.on_render_palette_popup_body is not None

    def _begin_drag_spawn(self, pin_id: ed.PinId) -> None:
        """Capture the dropped wire and open the palette popup with a
        compatibility filter pre-set."""
        fn_input, param_name = self._function_node_gui_from_input_pin_id(pin_id)
        if fn_input is not None:
            pin_type = fn_input.get_function_node().function_with_gui.input(param_name)._type
            if pin_type is None:
                return
            self._pending_drag_spawn = _PendingDragSpawn(pin_id, "input", pin_type, imgui.get_mouse_pos())
            self._palette_popup_just_requested = True
            return
        fn_output, output_idx = self._function_node_gui_from_output_pin_id(pin_id)
        if fn_output is not None:
            pin_type = fn_output.get_function_node().function_with_gui.output(output_idx)._type
            if pin_type is None:
                return
            self._pending_drag_spawn = _PendingDragSpawn(pin_id, "output", pin_type, imgui.get_mouse_pos())
            self._palette_popup_just_requested = True

    def _begin_background_palette_popup(self) -> None:
        """Open the palette popup at the cursor (no compatibility filter)."""
        self._bg_popup_screen_pos = imgui.get_mouse_pos()
        self._palette_popup_just_requested = True

    def _draw_palette_popup(self) -> bool:
        """Render the shared palette popup. Returns True if a node was spawned."""
        if self._pending_drag_spawn is None and self._bg_popup_screen_pos is None:
            return False
        on_open = self.on_open_palette_popup
        on_render = self.on_render_palette_popup_body
        if on_open is None or on_render is None:
            self._reset_palette_popup_state()
            return False

        if self._palette_popup_just_requested:
            compat: Optional[PaletteCompat] = None
            if self._pending_drag_spawn is not None:
                compat = (self._pending_drag_spawn.pin_type, self._pending_drag_spawn.pin_kind)
            on_open(compat)
            imgui.open_popup(self._PALETTE_POPUP_ID)
            self._palette_popup_just_requested = False

        # Force the popup width on appearance so the tag-checkbox grid wraps
        # to a readable column count instead of stretching across the screen.
        # (set_next_window_size_constraints alone is not enough — _gui_tags
        # reads content_region_avail to pick its column count before the
        # constraint can clamp the auto-grown popup.)
        popup_w = hello_imgui.em_size(self._PALETTE_POPUP_WIDTH_EM)
        max_h = hello_imgui.em_size(self._PALETTE_POPUP_MAX_HEIGHT_EM)
        imgui.set_next_window_size(ImVec2(popup_w, 0), imgui.Cond_.appearing)
        imgui.set_next_window_size_constraints(ImVec2(popup_w, 0), ImVec2(popup_w, max_h))

        spawned = False
        if imgui.begin_popup(self._PALETTE_POPUP_ID):
            picked: List[FunctionWithGui] = []
            on_render(picked.append)
            if picked:
                self._spawn_from_palette(picked[0])
                spawned = True
                imgui.close_current_popup()
            imgui.end_popup()
        else:
            self._reset_palette_popup_state()
        return spawned

    def _reset_palette_popup_state(self) -> None:
        self._pending_drag_spawn = None
        self._bg_popup_screen_pos = None
        self._palette_popup_just_requested = False

    def _spawn_from_palette(self, new_fn: FunctionWithGui) -> None:
        """Place the picked function on the canvas, and (if the popup was
        opened by a wire drop) wire it to the dragged pin."""
        pending = self._pending_drag_spawn
        screen_pos = pending.screen_pos if pending is not None else self._bg_popup_screen_pos
        self._reset_palette_popup_state()

        self.add_function_with_gui(new_fn)
        new_node_gui = self.function_nodes_gui[-1]
        if screen_pos is not None:
            self._pending_node_position = (new_node_gui.node_id(), ed.screen_to_canvas(screen_pos))

        if pending is not None:
            self._link_dragged_pin_to_new_node(pending, new_node_gui)

    def _link_dragged_pin_to_new_node(self, pending: _PendingDragSpawn, new_node_gui: FunctionNodeGui) -> None:
        new_fn_with_gui = new_node_gui.get_function_node().function_with_gui
        if pending.pin_kind == "output":
            for i in range(new_fn_with_gui.nb_inputs()):
                p = new_fn_with_gui.input_of_idx(i)
                t = p.data_with_gui._type
                if t is None or not is_link_compatible(pending.pin_type, t):
                    continue
                fn_output, src_output_idx = self._function_node_gui_from_output_pin_id(pending.pin_id)
                if fn_output is None:
                    return
                self._try_add_link_from_to(
                    fn_output.get_function_node(),
                    new_node_gui.get_function_node(),
                    dst_input_name=p.name,
                    src_output_idx=src_output_idx,
                )
                return
        else:
            for i in range(new_fn_with_gui.nb_outputs()):
                t = new_fn_with_gui.output(i)._type
                if t is None or not is_link_compatible(t, pending.pin_type):
                    continue
                fn_input, dst_param_name = self._function_node_gui_from_input_pin_id(pending.pin_id)
                if fn_input is None:
                    return
                self._try_add_link_from_to(
                    new_node_gui.get_function_node(),
                    fn_input.get_function_node(),
                    dst_input_name=dst_param_name,
                    src_output_idx=i,
                )
                return

    def _try_add_link_from_to(
        self, src_fn: FunctionNode, dst_fn: FunctionNode, *, dst_input_name: str, src_output_idx: int
    ) -> None:
        try:
            self.functions_graph._add_link_from_function_nodes(
                src_fn, dst_fn, dst_input_name=dst_input_name, src_output_idx=src_output_idx
            )
            self.functions_links_gui.append(
                FunctionNodeLinkGui(self.functions_graph.functions_nodes_links[-1], self.function_nodes_gui)
            )
        except ValueError as e:
            logging.warning(f"Palette-spawn link rejected: {e}")

    def _apply_pending_node_position(self) -> None:
        if self._pending_node_position is None:
            return
        node_id, pos = self._pending_node_position
        ed.set_node_position(node_id, pos)
        self._pending_node_position = None

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

    def did_any_focused_window_change_something(self) -> bool:
        frame_count = imgui.get_frame_count()
        # changed = any(fn.focused_window_change_frame_id == frame_count for fn in self.function_nodes_gui)
        changed = False
        for fn in self.function_nodes_gui:
            if fn._focused_window_change_frame_id == frame_count:
                changed = True
        return changed

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
        for name, fn_node_with_gui in self._dict_function_nodes().items():
            function_gui_settings_dict[name] = {
                "function_node_with_gui": fn_node_with_gui.save_gui_options_to_json(),
                "function_node": fn_node_with_gui.get_function_node().save_gui_options_to_json(),
            }
        return function_gui_settings_dict

    def load_gui_options_from_json(self, json_dict: JsonDict) -> None:
        for name, fn_node_with_gui in self._dict_function_nodes().items():
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
