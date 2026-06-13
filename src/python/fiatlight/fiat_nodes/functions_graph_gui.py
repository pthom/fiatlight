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
from fiatlight.fiat_nodes.sugiyama_layout import compute_layered_ranks, order_layers_to_reduce_crossings
from fiatlight.fiat_palette import (
    FunctionInfo,
    FunctionPalette,
    PaletteFilter,
    PinKind,
    palette_gui_body,
)
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_node_editor as ed, hello_imgui, ImVec2, imgui_ctx
from typing import List, Dict, Tuple


@dataclass(frozen=True)
class _DraggedFnParamPin:
    """The pin from which the user dragged the wire that opened the popup —
    used to wire the link once the new node is spawned."""

    pin_id: ed.PinId
    pin_kind: PinKind
    pin_type: TypeLike


@dataclass
class _OpenPalettePopup:
    """All state of the function-palette popup while it is open. Lives on
    `FunctionsGraphGui` for as long as the popup is showing; cleared on
    dismiss or pick.

    `canvas_pos` is where the new node should land. Pre-converted via
    `ed.screen_to_canvas` at the moment the popup is opened, *while inside*
    `ed.begin/end` — converting later, after `ed.end()`, gives stale or
    wrong canvas coords."""

    canvas_pos: ImVec2
    filter: PaletteFilter
    focus_search: bool = True
    pin: _DraggedFnParamPin | None = None  # set when entry was drag-from-pin
    just_requested: bool = True  # True until imgui.open_popup has been called once


class FunctionsGraphGui:
    # Palette popup geometry (em units, scaled by hello_imgui.em_size).
    _PALETTE_POPUP_WIDTH_EM = 50
    _PALETTE_POPUP_HEIGHT_EM = 40
    _PALETTE_POPUP_ID = "##palette_popup"

    functions_graph: FunctionsGraph

    function_nodes_gui: List[FunctionNodeGui]
    functions_links_gui: List[FunctionNodeLinkGui]

    shall_layout_graph: bool = False
    can_edit_graph: bool = False

    # Set by FiatGui (or any host) when a palette is available. When None,
    # the right-click / drag-from-pin popups don't appear.
    function_palette: FunctionPalette | None

    _idx_render_graph: int = 0
    _idx_last_frame_render: int = 0
    # The palette popup, if it is currently open (right-click on canvas OR drag-from-pin).
    _open_popup: _OpenPalettePopup | None = None
    # When a node is spawned from a popup, we need to set its position inside
    # an ed.begin/end block — defer to the next frame.
    _pending_node_position: Tuple[ed.NodeId, ImVec2] | None = None
    # Positions loaded from disk, applied lazily inside ed.begin/end on the
    # next draw, since `ed.set_node_position` is only valid in that scope.
    # Keyed by stable_id (the workspace format key).
    _pending_loaded_positions_by_stable_id: Dict[str, ImVec2] | None = None
    # ImGui frame at which a deferred `ed.navigate_to_content` should fire.
    # Two reasons it has to be deferred AND fired outside ed.begin/end:
    #   * `set_node_position` does not affect the bounds `navigate_to_content`
    #     reads until the next `ed.begin/end` cycle has run, so we wait one
    #     frame after applying positions.
    #   * `navigate_to_content` itself is only valid *outside* the active
    #     `ed.begin/end` block (calling it from inside is a no-op in this
    #     binding); we fire it after `ed.end()` from `draw()`.
    _navigate_after_load_frame: int | None = None
    # Screen-space top-left of the editor canvas widget, captured each frame
    # right before `ed.begin`. Combined with `ed.get_screen_size()` it gives
    # the canvas widget's screen rect, used by `_all_nodes_fit_in_canvas_view`.
    _canvas_screen_top_left: ImVec2 | None = None

    # ======================================================================================================================
    # Constructor
    # ======================================================================================================================
    def __init__(
        self,
        functions_graph: FunctionsGraph,
        function_palette: FunctionPalette | None = None,
    ) -> None:
        self.functions_graph = functions_graph
        self.function_palette = function_palette
        # Persistent across popup reopenings: the user's search / tags / category
        # / match mode are kept; only the per-open type filters are reset.
        self._palette_filter = PaletteFilter()
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

    def clear(self) -> None:
        """Empty the graph (data + GUI) and clear queued / transient state.
        Used by File > New: leaves the host with a fresh, empty canvas."""
        self.functions_graph.clear_all()
        self._create_function_nodes_and_links_gui()
        self._open_popup = None
        self._pending_node_position = None
        self._pending_loaded_positions_by_stable_id = None
        self._navigate_after_load_frame = None

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
            # Captured before ed.begin: after begin, get_cursor_screen_pos
            # would return a canvas-space coord, not the widget's screen TL.
            cursor = imgui.get_cursor_screen_pos()
            self._canvas_screen_top_left = ImVec2(cursor.x, cursor.y)
            ed.begin("FunctionsGraphGui")
            self._apply_pending_loaded_positions()
            self._apply_pending_node_position()
            if draw_nodes():
                nodes_changed = True
            draw_links()
            if self.can_edit_graph:
                self._handle_graph_edition()
            ed.end()
            # `navigate_to_content` is invalid inside ed.begin/end, so we
            # fire it here, after ed.end() but still inside the editor's
            # current-editor scope.
            self._apply_pending_navigate_to_content()
            fiat_node_semaphore._IS_RENDERING_IN_NODE = False
            if self.can_edit_graph:
                if self._draw_palette_popup():
                    nodes_changed = True
        self._idx_render_graph += 1
        return nodes_changed

    def _handle_graph_edition(self) -> None:
        # Inside ed.begin/end (and outside ed.begin_create), imgui-node-editor
        # reroutes imgui.get_mouse_pos() through its canvas transform: the
        # value below is already in canvas coordinates, NOT screen coordinates.
        # Inside ed.begin_create the transform is suspended and get_mouse_pos
        # returns true screen coords — see _open_popup_from_dragged_pin.
        mouse_canvas_pos = imgui.get_mouse_pos()
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
                if new_node_pin_id and self.function_palette is not None:
                    if ed.accept_new_item():
                        self._open_popup_from_dragged_pin(new_node_pin_id)
            ed.end_create()

        # Right-click on empty canvas → palette popup (no type filter).
        if self.function_palette is not None and ed.show_background_context_menu():
            self._open_popup_at(mouse_canvas_pos)

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
        self._collapse_linked_input(fn_input.get_function_node(), dst_param_name)

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
    class _GraphLayout_Section:  # Dummy class to create a section in the IDE # noqa
        """Auto-layout (Sugiyama columns), plus the pending-position / camera-refit
        plumbing that applies node positions and fits them into view. The pure
        layering / crossing-min algorithms live in `sugiyama_layout`."""

        pass

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
            self._layout_graph_layered()
            # Fit the whole laid-out graph into view, a few frames later (once
            # ed.end() has updated the node bounds the camera reads).
            self._navigate_after_load_frame = imgui.get_frame_count() + 3

    def _layout_graph_layered(self) -> None:
        """Sugiyama-style layered layout: place nodes in columns by their
        data-flow depth (sources left, sinks right), stacked within a column and
        spaced to their actual sizes. Left-to-right, so links run forward
        (output pin on the right -> input pin on the left). Within-column order is
        chosen to reduce link crossings (barycenter heuristic). Layering + ordering
        come from `sugiyama_layout`; here we turn columns into pixel positions."""
        nodes_gui = self.function_nodes_gui
        if not nodes_gui:
            return

        gui_by_sid: Dict[str, FunctionNodeGui] = {g.get_function_node().stable_id: g for g in nodes_gui}
        order: List[str] = [g.get_function_node().stable_id for g in nodes_gui]
        size_by_sid: Dict[str, ImVec2] = {sid: ed.get_node_size(g.node_id()) for sid, g in gui_by_sid.items()}

        edges = [
            (link.src_function_node.stable_id, link.dst_function_node.stable_id)
            for link in self.functions_graph.functions_nodes_links
        ]
        layer = compute_layered_ranks(order, edges)
        columns = order_layers_to_reduce_crossings(order, edges, layer)

        h_gap = hello_imgui.em_size(5)
        v_gap = hello_imgui.em_size(2)
        max_layer = max(layer.values())

        # Column widths (widest node) and heights (stacked), to space + center.
        col_width: Dict[int, float] = {}
        col_height: Dict[int, float] = {}
        for c in range(max_layer + 1):
            sids = columns[c]
            col_width[c] = max((size_by_sid[s].x for s in sids), default=0.0)
            col_height[c] = sum(size_by_sid[s].y for s in sids) + v_gap * max(0, len(sids) - 1)
        total_height = max(col_height.values(), default=0.0)

        x = 0.0
        for c in range(max_layer + 1):
            y = (total_height - col_height[c]) / 2.0  # center the column vertically
            for sid in columns[c]:
                ed.set_node_position(gui_by_sid[sid].node_id(), ImVec2(x, y))
                y += size_by_sid[sid].y + v_gap
            x += col_width[c] + h_gap

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
    def _open_popup_at(self, canvas_pos: ImVec2, dragged_pin: _DraggedFnParamPin | None = None) -> None:
        """Single entry point for both right-click and drag-from-pin.
        `canvas_pos` must already be in canvas coordinates."""
        # Reuse the persistent filter so the user's search / tags / category /
        # match mode survive closing and reopening the popup. Only the per-open
        # type filters (set by drag-from-pin) are reset each time.
        filt = self._palette_filter
        filt.input_type_filter = None
        filt.output_type_filter = None
        if dragged_pin is not None:
            if dragged_pin.pin_kind is PinKind.OUTPUT:
                filt.input_type_filter = dragged_pin.pin_type
            else:
                filt.output_type_filter = dragged_pin.pin_type
        # Defensive copy: ImVec2 is mutable and imgui.get_mouse_pos() may hand
        # back a reference that imgui mutates frame-to-frame.
        canvas_pos_copy = ImVec2(canvas_pos.x, canvas_pos.y)
        self._open_popup = _OpenPalettePopup(canvas_pos=canvas_pos_copy, filter=filt, pin=dragged_pin)

    def _open_popup_from_dragged_pin(self, pin_id: ed.PinId) -> None:
        """Resolve the pin id into kind + type, then open the popup."""
        fn_input, param_name = self._function_node_gui_from_input_pin_id(pin_id)
        if fn_input is not None:
            pin_type = fn_input.get_function_node().function_with_gui.input(param_name)._type
            if pin_type is None:
                return
            pin = _DraggedFnParamPin(pin_id, PinKind.INPUT, pin_type)
        else:
            fn_output, output_idx = self._function_node_gui_from_output_pin_id(pin_id)
            if fn_output is None:
                return
            pin_type = fn_output.get_function_node().function_with_gui.output(output_idx)._type
            if pin_type is None:
                return
            pin = _DraggedFnParamPin(pin_id, PinKind.OUTPUT, pin_type)
        # Inside ed.begin_create the editor suspends its canvas transform on
        # io.MousePos, so imgui.get_mouse_pos() returns true screen coords here.
        self._open_popup_at(ed.screen_to_canvas(imgui.get_mouse_pos()), dragged_pin=pin)

    def _draw_palette_popup(self) -> bool:
        """Render the popup and handle its lifecycle. Returns True if a node was spawned."""
        if self._open_popup is None or self.function_palette is None:
            return False
        popup = self._open_popup

        if popup.just_requested:
            imgui.open_popup(self._PALETTE_POPUP_ID)
            popup.just_requested = False

        # Force both width AND height on appearance: the side-by-side body
        # uses `imgui.get_content_region_avail()` to size the list/doc
        # children, which only works when the popup itself has a known size.
        popup_w = hello_imgui.em_size(self._PALETTE_POPUP_WIDTH_EM)
        popup_h = hello_imgui.em_size(self._PALETTE_POPUP_HEIGHT_EM)
        imgui.set_next_window_size(ImVec2(popup_w, popup_h), imgui.Cond_.appearing)

        spawned = False
        if imgui.begin_popup(self._PALETTE_POPUP_ID):
            picked: List[FunctionInfo] = []
            palette_gui_body(
                self.function_palette,
                popup.filter,
                on_pick=picked.append,
                focus_search=popup.focus_search,
            )
            popup.focus_search = False
            if picked:
                self._spawn_from_palette(picked[0].function_factory(), popup)
                spawned = True
                imgui.close_current_popup()
            imgui.end_popup()
        else:
            self._open_popup = None
        return spawned

    def _spawn_from_palette(self, new_fn: FunctionWithGui, popup: _OpenPalettePopup) -> None:
        """Place the picked function on the canvas, and (if the popup was
        opened by a wire drop) wire it to the dragged pin."""
        self._open_popup = None
        self.add_function_with_gui(new_fn)
        new_node_gui = self.function_nodes_gui[-1]
        self._pending_node_position = (new_node_gui.node_id(), popup.canvas_pos)
        if popup.pin is not None:
            self._link_dragged_pin_to_new_node(popup.pin, new_node_gui)

    def _link_dragged_pin_to_new_node(self, pin: _DraggedFnParamPin, new_node_gui: FunctionNodeGui) -> None:
        new_fn_with_gui = new_node_gui.get_function_node().function_with_gui
        if pin.pin_kind is PinKind.OUTPUT:
            for i in range(new_fn_with_gui.nb_inputs()):
                p = new_fn_with_gui.input_of_idx(i)
                t = p.data_with_gui._type
                if t is None or not is_link_compatible(pin.pin_type, t):
                    continue
                fn_output, src_output_idx = self._function_node_gui_from_output_pin_id(pin.pin_id)
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
                if t is None or not is_link_compatible(t, pin.pin_type):
                    continue
                fn_input, dst_param_name = self._function_node_gui_from_input_pin_id(pin.pin_id)
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
            self._collapse_linked_input(dst_fn, dst_input_name)
        except ValueError as e:
            logging.warning(f"Palette-spawn link rejected: {e}")

    @staticmethod
    def _collapse_linked_input(dst_fn: FunctionNode, dst_input_name: str) -> None:
        """Collapse a freshly-linked input to its one-line presentation: its
        value is driven from upstream and already shown on the source node's
        output, so the full (e.g. image) render would be redundant. Mirrors the
        default applied to linked inputs when a graph is loaded
        (FunctionNodeGui.__init__)."""
        param = dst_fn.function_with_gui.param(dst_input_name)
        param.data_with_gui._expanded = False

    def _apply_pending_node_position(self) -> None:
        if self._pending_node_position is None:
            return
        node_id, pos = self._pending_node_position
        ed.set_node_position(node_id, pos)
        self._pending_node_position = None

    def _apply_pending_loaded_positions(self) -> None:
        """Apply positions queued by `load_workspace_from_json`. Called from
        `draw()` inside `ed.begin/end`, the only context where
        `ed.set_node_position` is allowed. The matching camera-refit is
        scheduled here but fires from `_apply_pending_navigate_to_content`
        outside the editor block (see field comment)."""
        if self._pending_loaded_positions_by_stable_id is None:
            return
        for fn in self.function_nodes_gui:
            sid = fn.get_function_node().stable_id
            saved = self._pending_loaded_positions_by_stable_id.get(sid)
            if saved is not None:
                ed.set_node_position(fn.node_id(), saved)
        self._pending_loaded_positions_by_stable_id = None
        # Wait one frame: `navigate_to_content` reads node bounds that
        # don't reflect the just-applied positions until ed.end() has run.
        self._navigate_after_load_frame = imgui.get_frame_count() + 3

    def _apply_pending_navigate_to_content(self) -> None:
        """Fire the camera-refit scheduled by `_apply_pending_loaded_positions`.
        Must be called outside `ed.begin/end`."""
        if self._navigate_after_load_frame is None:
            return
        if imgui.get_frame_count() < self._navigate_after_load_frame:
            return
        if not self._all_nodes_fit_in_canvas_view():
            ed.navigate_to_content(0.05)
        self._navigate_after_load_frame = None

    def _all_nodes_fit_in_canvas_view(self) -> bool:
        """True if every node's screen-space rect lies fully inside the canvas widget's current screen rect."""
        if self._canvas_screen_top_left is None or len(self.function_nodes_gui) == 0:
            return False
        canvas_size = ed.get_screen_size()
        canvas_min = self._canvas_screen_top_left
        canvas_max = ImVec2(canvas_min.x + canvas_size.x, canvas_min.y + canvas_size.y)
        for fn in self.function_nodes_gui:
            node_id = fn.node_id()
            node_canvas_tl = ed.get_node_position(node_id)
            node_canvas_br = node_canvas_tl + ed.get_node_size(node_id)
            node_screen_tl = ed.canvas_to_screen(node_canvas_tl)
            node_screen_br = ed.canvas_to_screen(node_canvas_br)
            if (
                node_screen_tl.x < canvas_min.x
                or node_screen_tl.y < canvas_min.y
                or node_screen_br.x > canvas_max.x
                or node_screen_br.y > canvas_max.y
            ):
                return False
        return True

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
        # Workspace JSON: everything needed to reconstruct what the user sees
        # (nodes, links, values, per-pin GUI option blobs, node positions,
        # expand flags, focused-mode visibility). Shareable between machines.
        # ======================================================================================================================
        """

        pass

    _WORKSPACE_VERSION = 1
    _WORKSPACE_EXPAND_FIELDS = (
        "_inputs_expanded",
        "_outputs_expanded",
        "_doc_expanded",
        "fiat_tuning_expanded",
        "_internal_state_gui_expanded",
        "_backup_expanded_states",
    )

    def nodes_layout_signature(self) -> Tuple[Tuple[str, int, int], ...]:
        """A cheap fingerprint of node identities + canvas positions. Used to
        detect when an edit / node-drag has settled (vs. re-serializing the whole
        graph every frame). Rounded to ignore sub-pixel jitter."""
        sig = []
        for fn_node_gui in self.function_nodes_gui:
            sid = str(fn_node_gui.get_function_node().stable_id)
            pos = ed.get_node_position(fn_node_gui.node_id())
            sig.append((sid, round(pos.x), round(pos.y)))
        return tuple(sig)

    def save_workspace_to_json(self) -> JsonDict:
        """Build the full workspace dict: the core data from FunctionsGraph
        plus the GUI-layer fields each node carries (canvas position, expand
        flags, focused-mode visibility). The result is what gets written to
        `<app>.fiat_workspace.json`."""
        core = self.functions_graph.save_workspace_core_to_json()
        nodes = core["nodes"]
        for fn_node_gui in self.function_nodes_gui:
            sid = fn_node_gui.get_function_node().stable_id
            entry = nodes.get(sid)
            if entry is None:
                continue
            pos = ed.get_node_position(fn_node_gui.node_id())
            entry["position"] = [pos.x, pos.y]
            entry["expand_flags"] = self._save_expand_flags(fn_node_gui)
            entry["focused_function_visible"] = bool(fn_node_gui._focused_function_visible)
        return {"version": self._WORKSPACE_VERSION, **core}

    def load_workspace_from_json(
        self,
        json_data: JsonDict,
        function_factory_from_ref: FunctionWithGuiFactoryFromName,
        *,
        rebuild_topology: bool = True,
    ) -> None:
        """Inverse of `save_workspace_to_json`. ``rebuild_topology=False`` is
        the programmatic-mode path: the graph is already built from code, we
        only restore per-node values + GUI options + position + expand flags.

        Positions are queued for deferred application inside `ed.begin/end`.
        """
        version = json_data.get("version", 1)
        if isinstance(version, int) and version > self._WORKSPACE_VERSION:
            raise ValueError(
                f"Workspace version {version} is newer than this build supports ({self._WORKSPACE_VERSION})."
            )

        self.functions_graph.load_workspace_core_from_json(
            json_data, function_factory_from_ref, rebuild_topology=rebuild_topology
        )
        if rebuild_topology:
            self._create_function_nodes_and_links_gui()

        nodes_data = json_data.get("nodes", {})
        pending_positions: Dict[str, ImVec2] = {}
        for fn_node_gui in self.function_nodes_gui:
            sid = fn_node_gui.get_function_node().stable_id
            node_data = nodes_data.get(sid)
            if not isinstance(node_data, dict):
                continue
            pos = node_data.get("position")
            if isinstance(pos, list) and len(pos) == 2:
                pending_positions[sid] = ImVec2(float(pos[0]), float(pos[1]))
            expand_flags = node_data.get("expand_flags")
            if isinstance(expand_flags, dict):
                self._load_expand_flags(fn_node_gui, expand_flags)
            focused = node_data.get("focused_function_visible")
            if isinstance(focused, bool):
                fn_node_gui._focused_function_visible = focused
        # Reuse PR 2's queue mechanism: applied inside ed.begin/end on the
        # next draw. Stable-id keying is wired through
        # `_apply_pending_loaded_positions_by_stable_id` below.
        self._pending_loaded_positions_by_stable_id = pending_positions or None

    @classmethod
    def _save_expand_flags(cls, fn_node_gui: FunctionNodeGui) -> JsonDict:
        out: JsonDict = {}
        for field in cls._WORKSPACE_EXPAND_FIELDS:
            value = getattr(fn_node_gui, field)
            out[field] = value.save_to_dict()
        return out

    @classmethod
    def _load_expand_flags(cls, fn_node_gui: FunctionNodeGui, data: JsonDict) -> None:
        from fiatlight.fiat_nodes.value_in_node_vs_focused import (
            ExpandedFlagInNodeVsFocused,
            FlagsDictInNodeVsFocused,
        )

        for field in cls._WORKSPACE_EXPAND_FIELDS:
            if field not in data:
                continue
            if field == "_backup_expanded_states":
                setattr(fn_node_gui, field, FlagsDictInNodeVsFocused.load_from_dict(data[field]))
            else:
                setattr(fn_node_gui, field, ExpandedFlagInNodeVsFocused.load_from_dict(data[field]))
