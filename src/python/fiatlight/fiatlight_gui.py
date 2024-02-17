from fiatlight.fiatlight_types import MixedFunctionsGraph
from fiatlight import versatile
from fiatlight.functions_composition_graph import FunctionsCompositionGraph, FunctionNode
from fiatlight.internal import osd_widgets
from imgui_bundle import immapp, imgui, imgui_ctx
from typing import Any
from imgui_bundle import hello_imgui, ImVec4, ImVec2, immvision

from typing import List, Tuple


class FiatlightGuiParams:
    initial_value: Any
    functions_graph: MixedFunctionsGraph | None
    show_image_inspector: bool
    runner_params: hello_imgui.RunnerParams
    addons: immapp.AddOnsParams

    def __init__(
        self,
        functions_graph: MixedFunctionsGraph | None = None,
        app_title: str = "fiatlight",
        window_size: Tuple[int, int] | None = None,
        initial_value: Any = None,
        show_image_inspector: bool = False,
        runner_params: hello_imgui.RunnerParams | None = None,
        addons: immapp.AddOnsParams | None = None,
    ) -> None:
        self.functions_graph = functions_graph
        self.initial_value = initial_value
        self.show_image_inspector = show_image_inspector

        if addons is None:
            addons = immapp.AddOnsParams()
        self.addons = addons
        addons.with_node_editor = True

        if runner_params is None:
            runner_params = hello_imgui.RunnerParams()
        self.runner_params = runner_params
        assert runner_params is not None

        if len(runner_params.app_window_params.window_title) == 0:
            runner_params.app_window_params.window_title = app_title

        runner_params.app_window_params.window_geometry.size = window_size or (1600, 1000)

        runner_params.imgui_window_params.default_imgui_window_type = (
            hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
        )

        if runner_params is None:
            runner_params.app_window_params.restore_previous_geometry = True
            runner_params.imgui_window_params.show_status_bar = True
            runner_params.imgui_window_params.enable_viewports = True
            runner_params.imgui_window_params.show_menu_bar = True
            runner_params.imgui_window_params.show_menu_view = True

        self._runner_params = runner_params


class FiatlightGui:
    params: FiatlightGuiParams
    _functions_composition_graph: FunctionsCompositionGraph
    _main_dock_space_id: str
    _info_dock_space_id: str = "info_dock"
    _idx_frame: int = 0

    def __init__(self, params: FiatlightGuiParams) -> None:
        self.params = params
        if self.params.functions_graph is not None:
            functions_with_gui = [versatile.to_function_with_gui(f) for f in self.params.functions_graph]
        else:
            functions_with_gui = []
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
                    details_gui = osd_widgets.get_detail_gui()
                    if details_gui is not None:
                        details_gui()
                    imgui.end_tab_item()
                if imgui.begin_tab_item_simple("Exceptions"):
                    self._draw_exceptions()
                    imgui.end_tab_item()
                imgui.end_tab_bar()

    def _draw_functions_graph(self) -> None:
        self._idx_frame += 1
        if self._idx_frame == 1:
            hello_imgui.get_runner_params().docking_params.focus_dockable_window("Functions Graph")
        if self._idx_frame >= 3:
            # the window size is not available on the first frames,
            # and the node editor uses it to compute the initial position of the nodes
            # window_size = imgui.get_window_size()
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
        r = [main_window, info_window]
        if self.params.show_image_inspector:
            image_inspector = hello_imgui.DockableWindow(
                label_="Image Inspector",
                dock_space_name_=self._main_dock_space_id,
                gui_function_=lambda: immvision.inspector_show(),
            )
            r.append(image_inspector)
        return r

    def _docking_splits(self, initial_dock: str = "MainDockSpace") -> List[hello_imgui.DockingSplit]:
        self._main_dock_space_id = initial_dock
        split_main_info = hello_imgui.DockingSplit(
            initial_dock_=self._main_dock_space_id,
            new_dock_=self._info_dock_space_id,
            direction_=imgui.Dir_.down,
            ratio_=0.25,
        )
        return [split_main_info]

    def run(self) -> None:
        self._functions_composition_graph.set_input(self.params.initial_value)

        self.params.runner_params.docking_params.docking_splits += self._docking_splits()
        self.params.runner_params.docking_params.dockable_windows += self._dockable_windows()
        immapp.run(self.params.runner_params, self.params.addons)


def fiatlight_run(params: FiatlightGuiParams) -> None:
    fiatlight_gui = FiatlightGui(params)
    fiatlight_gui.run()
