from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui
from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui
from fiatlight.fiat_core import FunctionsGraph
from fiatlight.fiat_widgets import osd_widgets, fontawesome_6_ctx, icons_fontawesome_6
from fiatlight.fiat_utils import functional_utils
from imgui_bundle import immapp, imgui, imgui_ctx, ImVec4, portable_file_dialogs as pfd
from typing import Any, Callable
from imgui_bundle import hello_imgui, ImVec2, immvision

import json
import logging
import pathlib
from typing import List, Tuple


def _main_python_module_name() -> str:
    import inspect

    frame = inspect.currentframe()
    while frame:
        module = inspect.getmodule(frame)
        module_name = module.__name__ if module is not None else None
        if module_name != "__main__":
            frame = frame.f_back
        else:
            frame_full_file = frame.f_code.co_filename
            main_python_module_name = pathlib.Path(frame_full_file).stem
            return main_python_module_name
    return "fiatlight"


class FiatGuiParams:
    runner_params: hello_imgui.RunnerParams
    addons: immapp.AddOnsParams

    def __init__(
        self,
        app_title: str = "",
        window_size: Tuple[int, int] | None = None,
        initial_value: Any = None,
        runner_params: hello_imgui.RunnerParams | None = None,
        addons: immapp.AddOnsParams | None = None,
    ) -> None:
        self.initial_value = initial_value

        if addons is None:
            addons = immapp.AddOnsParams()
        self.addons = addons
        addons.with_node_editor = True

        created_runner_params = runner_params is None
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

        if created_runner_params:
            runner_params.app_window_params.restore_previous_geometry = True
            runner_params.imgui_window_params.show_status_bar = True
            runner_params.imgui_window_params.enable_viewports = True
            runner_params.imgui_window_params.show_menu_bar = True
            runner_params.imgui_window_params.show_menu_view = True

        self._runner_params = runner_params


class FiatGui:
    params: FiatGuiParams
    _functions_graph_gui: FunctionsGraphGui
    _main_dock_space_id: str
    _info_dock_space_id: str = "info_dock"
    _idx_frame: int = 0
    _show_inspector: bool = False

    save_dialog: pfd.save_file | None = None
    save_dialog_callback: Callable[[str], None] | None = None
    load_dialog: pfd.open_file | None = None
    load_dialog_callback: Callable[[str], None] | None = None

    def __init__(self, functions_graph: FunctionsGraph, params: FiatGuiParams | None = None) -> None:
        if params is None:
            # params.runner_params.app_window_params.window_title
            params = FiatGuiParams()

        # Set window_title from the name of the calling module
        if params.runner_params.app_window_params.window_title == "":
            params.runner_params.app_window_params.window_title = _main_python_module_name()

        self.params = params
        self._functions_graph_gui = FunctionsGraphGui(functions_graph)

    def _function_nodes(self) -> List[FunctionNodeGui]:
        return self._functions_graph_gui.function_nodes_gui

    def _has_one_exception(self) -> bool:
        return any(
            fn.function_node.function_with_gui.last_exception_message is not None for fn in self._function_nodes()
        )

    def _draw_exceptions(self) -> None:
        for function_node_gui in self._function_nodes():
            from fiatlight.fiat_runner import FIATLIGHT_GUI_CONFIG

            last_exception_message = function_node_gui.function_node.function_with_gui.last_exception_message
            last_exception_traceback = function_node_gui.function_node.function_with_gui.last_exception_traceback
            if last_exception_message is not None:
                function_unique_name = self._functions_graph_gui.functions_graph.function_node_unique_name(
                    function_node_gui.function_node
                )
                imgui.text_colored(
                    FIATLIGHT_GUI_CONFIG.colors.error,
                    f"Exception in {function_unique_name}: {last_exception_message}",
                )
                if last_exception_traceback is not None:
                    msg = last_exception_traceback
                    nb_lines = msg.count("\n") + 1
                    text_size = ImVec2(imgui.get_window_width(), immapp.em_size(nb_lines))
                    imgui.input_text_multiline("##error", msg, text_size)

    def _top_toolbar(self) -> None:
        btn_size = hello_imgui.em_to_vec2(2, 2)
        layout_width = imgui.get_window_width() - hello_imgui.em_size(0.5)
        with imgui_ctx.begin_horizontal("TopToolbar", ImVec2(layout_width, 0)):
            with fontawesome_6_ctx():
                # Layout graph
                if imgui.button(icons_fontawesome_6.ICON_FA_SITEMAP, btn_size):
                    self._functions_graph_gui.shall_layout_graph = True
                if imgui.is_item_hovered():
                    imgui.set_tooltip("Layout graph")

                imgui.spring()

                # Load and save user inputs
                if imgui.button(icons_fontawesome_6.ICON_FA_FILE_IMPORT, btn_size):
                    self.load_dialog = pfd.open_file(title="Load user inputs")
                    self.load_dialog_callback = lambda filename: self._load_user_inputs(filename)
                if imgui.is_item_hovered():
                    imgui.set_tooltip("Load user inputs")
                if imgui.button(icons_fontawesome_6.ICON_FA_FILE_PEN, btn_size):
                    self.save_dialog = pfd.save_file(title="Save user inputs")
                    self.save_dialog_callback = lambda filename: self._save_user_inputs(filename)
                if imgui.is_item_hovered():
                    imgui.set_tooltip("Save user inputs")

    def _draw_functions_graph(self) -> None:
        self._idx_frame += 1
        if self._idx_frame == 1:
            hello_imgui.get_runner_params().docking_params.focus_dockable_window("Functions Graph")
        if self._idx_frame >= 3:
            # the window size is not available on the first frames,
            # and the node editor uses it to compute the initial position of the nodes
            # window_size = imgui.get_window_size()
            self._functions_graph_gui.draw()

        osd_widgets.render()
        self._handle_file_dialogs()

    def _handle_file_dialogs(self) -> None:
        if self.save_dialog is not None and self.save_dialog.ready():
            selected_filename = self.save_dialog.result()
            if len(selected_filename) > 0:
                if self.save_dialog_callback is not None:
                    self.save_dialog_callback(selected_filename)
            self.save_dialog = None

        if self.load_dialog is not None and self.load_dialog.ready():
            selected_filenames = self.load_dialog.result()
            if len(selected_filenames) > 0:
                if self.load_dialog_callback is not None:
                    self.load_dialog_callback(selected_filenames[0])
            self.load_dialog = None

    def _dockable_windows(self) -> List[hello_imgui.DockableWindow]:
        main_window = hello_imgui.DockableWindow(
            label_="Functions Graph",
            dock_space_name_=self._main_dock_space_id,
            gui_function_=lambda: self._draw_functions_graph(),
        )
        image_inspector = hello_imgui.DockableWindow(
            label_="Image Inspector",
            dock_space_name_=self._main_dock_space_id,
            gui_function_=lambda: immvision.inspector_show(),
            # is_visible_=False,
        )
        r = [main_window, image_inspector]
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

    def _node_state_filename(self) -> str:
        return hello_imgui.ini_settings_location(self.params.runner_params)[:-4] + ".fiatlight.json"

    def _save_user_inputs(self, filename: str) -> None:
        has_extension = "." in filename
        if not has_extension:
            filename += ".fiatlight.json"

        json_data = self._functions_graph_gui.save_user_inputs_to_json()
        try:
            with open(filename, "w") as f:
                json_str = json.dumps(json_data, indent=4)
                f.write(json_str)
        except Exception as e:
            logging.error(f"FiatGui: Error saving state file {self._node_state_filename()}: {e}")

    def _load_user_inputs(self, filename: str) -> None:
        try:
            with open(filename, "r") as f:
                json_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.info(f"FiatGui: state file {self._node_state_filename()} not found, using default state")
            return

        try:
            self._functions_graph_gui.load_user_inputs_from_json(json_data)
            self._functions_graph_gui.functions_graph.invoke_top_leaf_functions()
        except Exception as e:
            logging.error(f"FiatGui: Error loading state file {self._node_state_filename()}: {e}")

    def _post_init(self) -> None:
        self._load_user_inputs(self._node_state_filename())

    def run(self) -> None:
        self.params.runner_params.docking_params.docking_splits += self._docking_splits()
        self.params.runner_params.docking_params.dockable_windows += self._dockable_windows()

        self.params.runner_params.callbacks.before_exit = functional_utils.sequence_void_functions(
            lambda: self._save_user_inputs(self._node_state_filename()), self.params.runner_params.callbacks.before_exit
        )
        self.params.runner_params.callbacks.post_init = functional_utils.sequence_void_functions(
            self._post_init, self.params.runner_params.callbacks.post_init
        )

        from fiatlight.fiat_widgets.fontawesome6_ctx_utils import _load_font_awesome_6

        self.params.runner_params.callbacks.load_additional_fonts = functional_utils.sequence_void_functions(
            hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons, _load_font_awesome_6
        )

        top_toolbar_options = hello_imgui.EdgeToolbarOptions(size_em=2.4, window_bg=ImVec4(0.3, 0.3, 0.3, 1.0))
        self.params.runner_params.callbacks.add_edge_toolbar(
            edge_toolbar_type=hello_imgui.EdgeToolbarType.top,
            gui_function=lambda: self._top_toolbar(),
            options=top_toolbar_options,
        )

        immapp.run(self.params.runner_params, self.params.addons)


def fiat_run(functions_graph: FunctionsGraph, params: FiatGuiParams | None = None) -> None:
    fiat_gui = FiatGui(functions_graph, params)
    fiat_gui.run()