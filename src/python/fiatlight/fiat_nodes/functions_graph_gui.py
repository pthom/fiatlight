from __future__ import annotations


from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui, FunctionNodeLinkGui
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_node_editor as ed, hello_imgui, ImVec2, imgui_ctx
from typing import List, Dict, Tuple


class FunctionsGraphGui:
    functions_graph: FunctionsGraph

    function_nodes_gui: List[FunctionNodeGui]
    functions_links_gui: List[FunctionNodeLinkGui]

    shall_layout_graph: bool = False
    can_edit_graph: bool = True

    _idx_frame: int = 0

    def __init__(self, functions_graph: FunctionsGraph) -> None:
        self.functions_graph = functions_graph

        self.function_nodes_gui = []
        for f in self.functions_graph.functions_nodes:
            self.function_nodes_gui.append(FunctionNodeGui(f))

        self.functions_links_gui = []
        for link in self.functions_graph.functions_nodes_links:
            link_gui = FunctionNodeLinkGui(link, self.function_nodes_gui)
            self.functions_links_gui.append(link_gui)

    def add_function_with_gui(self, function: FunctionWithGui) -> None:
        function_node = self.functions_graph.add_function(function)
        function_node_gui = FunctionNodeGui(function_node)
        self.function_nodes_gui.append(function_node_gui)

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

    def draw(self) -> None:
        def draw_nodes() -> None:
            for fn in self.function_nodes_gui:
                imgui.push_id(str(id(fn)))
                fn.draw_node(self.functions_graph.function_node_unique_name(fn._function_node))  # noqa
                imgui.pop_id()

        def draw_links() -> None:
            for link in self.functions_links_gui:
                link.draw()

        self._layout_graph_if_required()
        with imgui_ctx.push_obj_id(self):
            ed.begin("FunctionsGraphGui")
            draw_nodes()
            draw_links()
            if self.can_edit_graph:
                self._handle_links_edit()
            ed.end()
        self._idx_frame += 1

    def _function_node_gui_from_id(self, node_id: ed.NodeId) -> FunctionNodeGui:
        matching_nodes = [fn for fn in self.function_nodes_gui if fn.node_id() == node_id]
        if len(matching_nodes) == 0:
            raise ValueError(f"Node with id {node_id} not found")
        assert len(matching_nodes) == 1
        return matching_nodes[0]

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

    def _handle_links_edit(self) -> None:
        # Handle creation action, returns true if editor want to create new object (node or link)
        if ed.begin_create():
            input_pin_id = ed.PinId()
            output_pin_id = ed.PinId()

            # QueryNewLink returns true if editor want to create new link between pins.
            if ed.query_new_link(input_pin_id, output_pin_id):
                # Link can be created only for two valid pins, it is up to you to
                # validate if connection make sense. Editor is happy to make any.
                #
                # Link always goes from input to output. User may choose to drag
                # link from output pin or input pin. This determines which pin ids
                # are valid and which are not:
                #   * input valid, output invalid - user started to drag new link from input pin
                #   * input invalid, output valid - user started to drag new link from output pin
                #   * input valid, output valid   - user dragged link over other pin, can be validated

                if input_pin_id and output_pin_id and input_pin_id != output_pin_id:
                    can_add_link, fail_reason = self._can_add_link(input_pin_id, output_pin_id)
                    if not can_add_link:
                        ed.reject_new_item()
                        fiat_osd.set_tooltip(fail_reason)
                    else:
                        if ed.accept_new_item():
                            self._try_add_link(input_pin_id, output_pin_id)

            ed.end_create()

        if ed.begin_delete():
            link_id = ed.LinkId()
            if ed.query_deleted_link(link_id):
                print("Delete link with id", link_id)
                # imgui.set_tooltip("Delete link with id " + str(link_id))
            #     if ed.accept_deleted_item():
            #         link = next(link for link in self.functions_links_gui if link.link_id() == link_id)
            #         self.functions_graph.remove_link(link.function_node_link)
            #         self.functions_links_gui.remove(link)
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
                    print("Delete link", link_context_menu_id)
                # imgui.open_popup("Link context menu")

            fiat_osd.set_popup_gui(show_link_context_menu)
            print("Show link context menu", link_context_menu_id)
            # imgui.open_popup("Link context menu")

        # ed.suspend()
        # if imgui.begin_popup("Link context menu"):
        #     print("Link context menu", link_context_menu_id)
        #     imgui.text("Link context menu")
        #     if imgui.menu_item("Inspect pin"):
        #         print("Inspect Link", link_context_menu_id)
        #     imgui.end_popup()
        # ed.resume()

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

        ok, failure_reason = self.functions_graph.can_add_link(
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

        ok, _failure_reason = self.functions_graph.can_add_link(
            fn_output.get_function_node(), fn_input.get_function_node(), dst_param_name, src_output_idx
        )
        if not ok:
            return False

        # 2. Create and add the links to the lists
        # We need to add
        # - a link to self.functions_graph.functions_nodes_links
        # - and a link to self.functions_links_gui
        function_node_link = self.functions_graph.add_link_from_function_nodes(
            fn_output.get_function_node(), fn_input.get_function_node(), dst_param_name, src_output_idx
        )
        function_node_link_gui = FunctionNodeLinkGui(function_node_link, self.function_nodes_gui)
        self.functions_links_gui.append(function_node_link_gui)

        return True

    def function_node_unique_name(self, function_node_gui: FunctionNodeGui) -> str:
        return self.functions_graph.function_node_unique_name(function_node_gui._function_node)  # noqa

    def function_node_with_unique_name(self, function_name: str) -> FunctionNodeGui:
        return next(fn for fn in self.function_nodes_gui if self.function_node_unique_name(fn) == function_name)

    def all_function_nodes_with_unique_names(self) -> Dict[str, FunctionNodeGui]:
        return {self.function_node_unique_name(fn): fn for fn in self.function_nodes_gui}

    def save_user_inputs_to_json(self) -> JsonDict:
        function_graph_dict = self.functions_graph.save_user_inputs_to_json()

        function_gui_settings_dict = {}
        for name, fn in self.all_function_nodes_with_unique_names().items():
            function_gui_settings_dict[name] = fn.save_gui_options_to_json()

        r = {
            "functions_graph": function_graph_dict,
            "functions_gui_settings": function_gui_settings_dict,
        }
        return r

    def load_user_inputs_from_json(self, json_data: JsonDict) -> None:
        self.functions_graph.load_user_inputs_from_json(json_data["functions_graph"])

        if "functions_gui_settings" in json_data:
            function_gui_settings_dict = json_data["functions_gui_settings"]
            for name, fn in self.all_function_nodes_with_unique_names().items():
                if name in function_gui_settings_dict:
                    fn.load_gui_options_from_json(function_gui_settings_dict[name])


def sandbox() -> None:
    def add(a: int, b: int = 2) -> int:
        return a + b

    def mul2(x: int) -> int:
        return x * 2

    def div3(x: int) -> float:
        return x / 3

    fg = FunctionsGraph.from_function_composition([add, mul2, div3])
    fgg = FunctionsGraphGui(fg)

    from imgui_bundle import immapp

    def gui() -> None:
        fgg.draw()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
