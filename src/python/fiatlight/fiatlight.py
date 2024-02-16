from fiatlight.fiatlight_types import MixedFunctionsGraph
from fiatlight import versatile
from fiatlight.functions_composition_graph import FunctionsCompositionGraph, FunctionNode
from fiatlight.internal import osd_widgets
from imgui_bundle import immapp, imgui, imgui_ctx
from typing import Any
from imgui_bundle import hello_imgui, ImVec4, ImVec2

from typing import List


class FiatlightGui:
    _functions_composition_graph: FunctionsCompositionGraph
    _main_dock_space_id: str
    _info_dock_space_id: str = "info_dock"
    _runner_params: hello_imgui.RunnerParams
    _first_frame: bool = True

    def __init__(self, functions_graph: MixedFunctionsGraph) -> None:
        functions_with_gui = [versatile.to_function_with_gui(f) for f in functions_graph]
        self._functions_composition_graph = FunctionsCompositionGraph(functions_with_gui)

    def _function_nodes(self) -> List[FunctionNode]:
        return self._functions_composition_graph.function_nodes

    def _has_one_exception(self) -> bool:
        return any(fn.last_exception_message is not None for fn in self._function_nodes())

    def _draw_exceptions(self) -> None:
        for function_node in self._function_nodes():
            if function_node.last_exception_message is not None:
                function_name = function_node.function.name()
                imgui.text_colored(
                    ImVec4(1, 0, 0, 1), f"Exception in {function_name}: {function_node.last_exception_message}"
                )
                if function_node.last_exception_traceback is not None:
                    msg = function_node.last_exception_traceback
                    nb_lines = msg.count("\n") + 1
                    text_size = ImVec2(imgui.get_window_width(), immapp.em_size(nb_lines))
                    imgui.input_text_multiline("##error", msg, text_size)

    def _draw_info_panel(self) -> None:
        osd_widgets.render()
        with imgui_ctx.push_obj_id(self):
            if imgui.begin_tab_bar("InfoPanelTabBar"):
                if imgui.begin_tab_item_simple("Info"):
                    imgui.text("This is the info panel")
                    imgui.end_tab_item()
                if imgui.begin_tab_item_simple("Exceptions"):
                    self._draw_exceptions()
                    imgui.end_tab_item()
                imgui.end_tab_bar()

    def _draw_functions_graph(self) -> None:
        if self._first_frame:
            # the window size is not available on the first frame
            self._first_frame = False
            return
        self._functions_composition_graph.draw()

    def _dockable_windows(self) -> List[hello_imgui.DockableWindow]:
        main_window = hello_imgui.DockableWindow(
            label_="Functions Graph",
            dock_space_name_=self._main_dock_space_id,
            gui_function_=lambda: self._draw_functions_graph(),
        )
        info_window = hello_imgui.DockableWindow(
            label_="Functions Graph Info",
            dock_space_name_=self._info_dock_space_id,
            gui_function_=lambda: self._draw_info_panel(),
        )
        return [main_window, info_window]

    def _docking_splits(self, initial_dock: str = "MainDockSpace") -> List[hello_imgui.DockingSplit]:
        self._main_dock_space_id = initial_dock
        split_main_info = hello_imgui.DockingSplit(
            initial_dock_=self._main_dock_space_id,
            new_dock_=self._info_dock_space_id,
            direction_=imgui.Dir_.down,
            ratio_=0.25,
        )
        return [split_main_info]

    def run(self, app_window_title: str, initial_value: Any) -> None:
        self._functions_composition_graph.set_input(initial_value)

        addons = immapp.AddOnsParams()
        addons.with_markdown = True
        addons.with_node_editor = True

        runner_params = hello_imgui.RunnerParams()

        runner_params.docking_params.docking_splits = self._docking_splits()
        runner_params.docking_params.dockable_windows = self._dockable_windows()

        runner_params.app_window_params.window_title = app_window_title
        runner_params.app_window_params.window_geometry.size = (1200, 900)
        runner_params.app_window_params.restore_previous_geometry = True

        runner_params.imgui_window_params.default_imgui_window_type = (
            hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
        )

        runner_params.imgui_window_params.show_status_bar = True
        runner_params.imgui_window_params.enable_viewports = True

        runner_params.imgui_window_params.show_menu_bar = True
        runner_params.imgui_window_params.show_menu_view = True

        self._runner_params = runner_params
        immapp.run(self._runner_params, addons)
