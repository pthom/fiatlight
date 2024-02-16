from fiatlight.fiatlight_types import MixedFunctionsGraph
from fiatlight import versatile
from fiatlight.functions_composition_graph import FunctionsCompositionGraph
from imgui_bundle import immapp, imgui
from typing import Any
from imgui_bundle import hello_imgui

from typing import List


class FiatlightGui:
    _functions_composition_graph: FunctionsCompositionGraph
    main_dock_space_id: str
    info_dock_space_id: str = "info_dock"

    def __init__(self, functions_graph: MixedFunctionsGraph) -> None:
        functions_with_gui = [versatile.to_function_with_gui(f) for f in functions_graph]
        self._functions_composition_graph = FunctionsCompositionGraph(functions_with_gui)

    def set_functions_composition_graph(self, functions_composition_graph: Any) -> None:
        self._functions_composition_graph = functions_composition_graph

    def _draw_info_panel(self) -> None:
        imgui.text("Info Panel")

    def _draw_functions_graph(self) -> None:
        self._functions_composition_graph.draw()

    def _dockable_windows(self) -> List[hello_imgui.DockableWindow]:
        main_window = hello_imgui.DockableWindow(
            label_="Functions Graph",
            dock_space_name_=self.main_dock_space_id,
            gui_function_=lambda: self._draw_functions_graph(),
        )
        info_window = hello_imgui.DockableWindow(
            label_="Info Panel", dock_space_name_=self.info_dock_space_id, gui_function_=lambda: self._draw_info_panel()
        )
        return [main_window, info_window]

    def _docking_splits(self, initial_dock: str = "MainDockSpace") -> List[hello_imgui.DockingSplit]:
        self.main_dock_space_id = initial_dock
        split_main_info = hello_imgui.DockingSplit(
            initial_dock_=self.main_dock_space_id,
            new_dock_=self.info_dock_space_id,
            direction_=imgui.Dir_.down,
            ratio_=0.25,
        )
        return [split_main_info]

    def run(self, app_window_title: str, initial_value: str) -> None:
        self._functions_composition_graph.set_input(initial_value)

        addons = immapp.AddOnsParams()
        addons.with_markdown = True
        addons.with_node_editor = True

        runner_params = hello_imgui.RunnerParams()
        runner_params.app_window_params.window_title = app_window_title
        runner_params.imgui_window_params.default_imgui_window_type = (
            hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
        )
        runner_params.docking_params.docking_splits = self._docking_splits()
        runner_params.docking_params.dockable_windows = self._dockable_windows()

        immapp.run(runner_params, addons)
