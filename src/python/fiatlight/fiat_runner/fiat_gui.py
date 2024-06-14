import traceback

from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui
from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui
from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_types.function_types import VoidFunction
from fiatlight.fiat_types.function_types import Function
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6, fiat_osd
from fiatlight.fiat_utils import functional_utils
from fiatlight.fiat_runner.functions_collection import FunctionCollectionGui
from fiatlight.fiat_kits.fiat_image.image_types import ImageU8_3
from imgui_bundle import immapp, imgui, imgui_ctx, ImVec4, portable_file_dialogs as pfd
from typing import Any, Callable
from imgui_bundle import hello_imgui, ImVec2, immvision

import json
import logging
import pathlib
from typing import List, Tuple
from enum import Enum, auto


class _EnqueuedCallbacks:
    frame_start: List[VoidFunction]
    frame_end: List[VoidFunction]

    def __init__(self) -> None:
        self.frame_start = []
        self.frame_end = []

    def enqueue_frame_start_callback(self, callback: VoidFunction) -> None:
        self.frame_start.append(callback)

    def enqueue_frame_end_callback(self, callback: VoidFunction) -> None:
        self.frame_end.append(callback)

    def run_pre_frame_callbacks(self) -> None:
        for callback in self.frame_start:
            callback()
        self.frame_start.clear()

    def run_post_frame_callbacks(self) -> None:
        for callback in self.frame_end:
            callback()
        self.frame_end.clear()


_ENQUEUED_CALLBACKS = _EnqueuedCallbacks()


def fire_once_at_frame_start(callback: VoidFunction) -> None:
    """Register a function that will be called once (and only once) at the start of the next frame."""
    _ENQUEUED_CALLBACKS.enqueue_frame_start_callback(callback)


def fire_once_at_frame_end(callback: VoidFunction) -> None:
    """Register a function that will be called once (and only once) at the end of the next frame."""
    _ENQUEUED_CALLBACKS.enqueue_frame_end_callback(callback)


def _is_running_in_notebook() -> bool:
    try:
        from IPython import get_ipython  # type: ignore  # noqa

        ipython = get_ipython()  # type: ignore
        if ipython is None:
            return False
        if "IPKernelApp" in get_ipython().config:  # type: ignore
            return True
    except ImportError:
        return False
    return False


def _is_running_in_documentation() -> bool:
    from fiatlight.fiat_config import fiatlight_doc_path
    import os

    cwd = os.path.abspath(os.getcwd())
    r = cwd.startswith(fiatlight_doc_path())
    return r


# ==================================================================================================================
#                                  Logging
# ==================================================================================================================
class HelloImGuiLogHandler(logging.Handler):
    def emit(self, record: Any) -> None:
        # Map the logging level to the LogLevel enum
        level = hello_imgui.LogLevel.info
        if record.levelno == logging.DEBUG:
            level = hello_imgui.LogLevel.debug
        elif record.levelno == logging.WARNING:
            level = hello_imgui.LogLevel.warning
        elif record.levelno == logging.ERROR:
            level = hello_imgui.LogLevel.error
        # Call the log function
        msg = self.format(record)
        hello_imgui.log(level, msg)


# Create a logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  # Or whatever level you want

# Create the HelloImGuiLogHandler
hello_imgui_log_handler = HelloImGuiLogHandler()
hello_imgui_log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
root_logger.addHandler(hello_imgui_log_handler)

# Create a console handler
if not _is_running_in_documentation():  # do not add logs to doc notebooks
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root_logger.addHandler(console_handler)

# Last image
_LAST_SCREENSHOT: ImageU8_3 | None = None


def get_last_screenshot() -> ImageU8_3 | None:
    """Returns a screenshot of the nodes of the last frame, just before exiting the app."""
    return _LAST_SCREENSHOT


# ==================================================================================================================
#                                  _main_python_module_name
#                      (used to set the window title and settings file name)
# ==================================================================================================================
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


def _ini_filename_from_app_name(app_name: str) -> str:
    app_name_sane = ""
    for c in app_name:
        if c.isalnum():
            app_name_sane += c
        else:
            app_name_sane += "_"
    return "fiat_settings/" + app_name_sane + ".ini"


# ==================================================================================================================
#                                  FiatGuiParams
# ==================================================================================================================
class FiatGuiParams:
    runner_params: hello_imgui.RunnerParams
    addons: immapp.AddOnsParams
    customizable_graph: bool = False

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
        addons.with_markdown = True
        addons.with_implot = True

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


# ==================================================================================================================
#                                  FiatGui
# ==================================================================================================================
class _SaveType(Enum):
    UserInputs = auto()
    GraphComposition = auto()


class FiatGui:
    # ==================================================================================================================
    #                                  Members
    # ==================================================================================================================
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

    _functions_collection_gui: FunctionCollectionGui

    _logo_image: ImageU8_3

    # ==================================================================================================================
    #                                  Constructor
    # ==================================================================================================================
    def __init__(
        self, functions_graph: FunctionsGraph, params: FiatGuiParams | None = None, app_name: str | None = None
    ) -> None:
        if params is None:
            params = FiatGuiParams()

        if app_name is not None:
            params.runner_params.app_window_params.window_title = app_name
        elif params.runner_params.app_window_params.window_title == "":
            # Set window_title from the name of the calling module
            params.runner_params.app_window_params.window_title = _main_python_module_name()

        if len(params.runner_params.ini_filename) == 0:
            params.runner_params.ini_filename = _ini_filename_from_app_name(
                params.runner_params.app_window_params.window_title
            )

        self.params = params
        self._functions_graph_gui = FunctionsGraphGui(functions_graph)

        if self.params.customizable_graph:
            self._functions_graph_gui.can_edit_graph = True

        self._functions_collection_gui = FunctionCollectionGui()

        self._functions_collection_gui.on_add_function = lambda fn: self._functions_graph_gui.add_function_with_gui(fn)

        # Read the logo image
        import cv2
        from fiatlight import demo_assets_dir

        logo_path = demo_assets_dir() + "/logo/logo1.jpg"
        self._logo_image = cv2.imread(logo_path)  # type: ignore

    # ==================================================================================================================
    #                                  Run
    # ==================================================================================================================
    class _Run_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def _post_init(self) -> None:
        self._load_graph_composition_at_startup()
        self._load_user_inputs_at_startup()
        self._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=False)
        self._notify_if_dirty_functions()
        self._disable_idling_if_any_live_function()

    def _before_exit(self) -> None:
        # print(f"settings file {self._user_settings_filename()} in {os.getcwd()}")
        self._store_final_app_window_screenshot()
        self._functions_graph_gui.on_exit()
        if self.params.customizable_graph:
            self._save_graph_composition(self._graph_composition_filename())
        self._save_user_inputs(self._user_settings_filename())

    @staticmethod
    def _pre_new_frame() -> None:
        _ENQUEUED_CALLBACKS.run_pre_frame_callbacks()

    @staticmethod
    def _after_swap() -> None:
        _ENQUEUED_CALLBACKS.run_post_frame_callbacks()

    def run(self) -> None:
        self.params.runner_params.docking_params.docking_splits += self._docking_splits()
        self.params.runner_params.docking_params.dockable_windows += self._dockable_windows()

        self.params.runner_params.callbacks.before_exit = functional_utils.sequence_void_functions(
            self._before_exit,
            self.params.runner_params.callbacks.before_exit,
        )
        self.params.runner_params.callbacks.post_init = functional_utils.sequence_void_functions(
            self._post_init, self.params.runner_params.callbacks.post_init
        )
        self.params.runner_params.callbacks.pre_new_frame = self._pre_new_frame
        self.params.runner_params.callbacks.after_swap = self._after_swap

        from fiatlight.fiat_widgets.fontawesome6_ctx_utils import _load_font_awesome_6  # noqa

        self.params.runner_params.callbacks.load_additional_fonts = functional_utils.sequence_void_functions(
            hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons, _load_font_awesome_6
        )

        top_toolbar_options = hello_imgui.EdgeToolbarOptions(size_em=2.5, window_bg=ImVec4(0.3, 0.3, 0.3, 1.0))
        self.params.runner_params.callbacks.add_edge_toolbar(
            edge_toolbar_type=hello_imgui.EdgeToolbarType.top,
            gui_function=lambda: self._top_toolbar(),
            options=top_toolbar_options,
        )

        self.params.runner_params.callbacks.post_render_dockable_windows = self._heartbeat_post_render_dockable_windows

        immapp.run(self.params.runner_params, self.params.addons)

    def _store_final_app_window_screenshot(self) -> None:
        global _LAST_SCREENSHOT
        last_hello_imgui_image = hello_imgui.final_app_window_screenshot()
        nodes_boundings = self._functions_graph_gui._get_node_screenshot_boundings()  # noqa
        last_nodes_image = last_hello_imgui_image[
            int(nodes_boundings.min.y) : int(nodes_boundings.max.y),
            int(nodes_boundings.min.x) : int(nodes_boundings.max.x),
        ]
        _LAST_SCREENSHOT = last_nodes_image  # type: ignore

    def _heartbeat_post_render_dockable_windows(self) -> None:
        fiat_osd._render_all_osd()  # noqa
        self._handle_file_dialogs()
        if self.params.customizable_graph:
            self._functions_collection_gui.gui()

    def _disable_idling_if_any_live_function(self) -> None:
        has_live_function = False
        for fn in self._functions_graph_gui.functions_graph.functions_nodes:
            if fn.function_with_gui.is_live():
                has_live_function = True
                break
        if has_live_function:
            self.params.runner_params.fps_idling.enable_idling = False

    # ==================================================================================================================
    #                                  GUI
    # ==================================================================================================================
    class _Gui_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    @staticmethod
    def _top_toolbar_btn_size() -> ImVec2:
        return hello_imgui.em_to_vec2(1.5, 1.5)

    def _panel_save_load_user_inputs(self) -> None:
        btn_size = self._top_toolbar_btn_size()
        with imgui_ctx.begin_horizontal("UserInputs"):
            if imgui.button(icons_fontawesome_6.ICON_FA_FILE_IMPORT, btn_size):
                self.load_dialog = pfd.open_file(title="Load user inputs")
                self.load_dialog_callback = self._load_user_inputs_during_execution
            if imgui.is_item_hovered():
                imgui.set_tooltip("Load user inputs")

            if imgui.button(icons_fontawesome_6.ICON_FA_FILE_PEN, btn_size):
                self.save_dialog = pfd.save_file(title="Save user inputs")
                self.save_dialog_callback = self._save_user_inputs
            if imgui.is_item_hovered():
                imgui.set_tooltip("Save user inputs")

    def _panel_save_load_graph_composition(self) -> None:
        btn_size = self._top_toolbar_btn_size()
        with imgui_ctx.begin_horizontal("GraphComposition"):
            if imgui.button(icons_fontawesome_6.ICON_FA_FILE_IMPORT, btn_size):
                self.load_dialog = pfd.open_file(title="Load graph definition")
                self.load_dialog_callback = self._load_graph_composition_during_execution
            if imgui.is_item_hovered():
                imgui.set_tooltip("Load graph definition")

            if imgui.button(icons_fontawesome_6.ICON_FA_FILE_PEN, btn_size):
                self.save_dialog = pfd.save_file(title="Save graph definition")
                self.save_dialog_callback = self._save_graph_composition
            if imgui.is_item_hovered():
                imgui.set_tooltip("Save graph definition")

    def _panel_graph(self) -> None:
        btn_size = self._top_toolbar_btn_size()
        with imgui_ctx.begin_horizontal("_panel_graph"):
            if imgui.button(icons_fontawesome_6.ICON_FA_SITEMAP, btn_size):
                self._functions_graph_gui.shall_layout_graph = True
            if imgui.is_item_hovered():
                imgui.set_tooltip("Layout graph")

    def _show_ribbon_dirty_if_needed(self) -> None:
        has_dirty_functions = self._functions_graph_gui.functions_graph.shall_display_refresh_needed_label()
        if not has_dirty_functions:
            return

        from fiatlight.fiat_widgets.ribbon_panel import ribbon_panel, vertical_separator  # noqa
        from fiatlight.fiat_config import FiatColorType, get_fiat_config

        def ribbon_fn() -> None:
            btn_size = self._top_toolbar_btn_size()
            dirty_color = get_fiat_config().style.color_as_vec4(FiatColorType.OutputValueDirty)
            with imgui_ctx.push_style_color(imgui.Col_.text.value, dirty_color):
                if imgui.button(icons_fontawesome_6.ICON_FA_ROTATE, btn_size):
                    self._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=True)
            if imgui.is_item_hovered():
                imgui.set_tooltip("Some functions needs to be refreshed! Click to recompute them.")

        ribbon_panel("Refresh!", ribbon_fn)
        vertical_separator()

    def _display_logo(self) -> None:
        with imgui_ctx.begin_vertical("Logo"):
            logo_display_size = self._top_toolbar_btn_size()
            logo_display_size_tuple = (int(logo_display_size.x), int(logo_display_size.y))
            immvision.image_display("##logo", self._logo_image, logo_display_size_tuple)
            if imgui.begin_item_tooltip():
                logo_display_size_big = int(hello_imgui.em_size(40))
                immvision.image_display("##logo_big", self._logo_image, (logo_display_size_big, logo_display_size_big))
                imgui.end_tooltip()
            imgui.text_disabled("fiatlight")

    def _top_toolbar(self) -> None:
        from fiatlight.fiat_widgets.ribbon_panel import ribbon_panel, vertical_separator  # noqa

        btn_size = self._top_toolbar_btn_size()

        layout_width = imgui.get_window_width() - hello_imgui.em_size(0.4)

        # Move the cursor up a bit
        cursor_pos = imgui.get_cursor_pos()
        cursor_pos.y -= hello_imgui.em_size(0.5)
        imgui.set_cursor_pos(cursor_pos)

        with imgui_ctx.begin_horizontal("TopToolbar", ImVec2(layout_width, 0)):
            with fontawesome_6_ctx():
                self._display_logo()
                imgui.dummy(ImVec2(hello_imgui.em_size(3), 0))

                # Layout graph
                ribbon_panel("Graph", self._panel_graph)
                vertical_separator()

                imgui.spring()
                vertical_separator()
                self._show_ribbon_dirty_if_needed()

                # Load and save user inputs
                ribbon_panel("User Inputs", self._panel_save_load_user_inputs)
                vertical_separator()

                if self.params.customizable_graph:
                    with imgui_ctx.push_id("GraphComposition"):
                        ribbon_panel("Graph", self._panel_save_load_graph_composition)
                        vertical_separator()

                if imgui.button(icons_fontawesome_6.ICON_FA_POWER_OFF, btn_size):
                    hello_imgui.get_runner_params().app_shall_exit = True
                if imgui.is_item_hovered():
                    imgui.set_tooltip("Exit")

    def _draw_functions_graph(self) -> None:
        self._idx_frame += 1
        if self._idx_frame == 1:
            hello_imgui.get_runner_params().docking_params.focus_dockable_window("Functions Graph")
        if self._idx_frame >= 3:
            # the window size is not available on the first frames,
            # and the node editor uses it to compute the initial position of the nodes
            # window_size = imgui.get_window_size()
            any_change = self._functions_graph_gui.draw()
            if any_change:
                self._notify_if_dirty_functions()

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
        logger_window = hello_imgui.DockableWindow(
            label_="Log", dock_space_name_=self._info_dock_space_id, gui_function_=lambda: hello_imgui.log_gui()
        )
        r = [main_window, image_inspector, logger_window]
        return r

    def _docking_splits(self, initial_dock: str = "MainDockSpace") -> List[hello_imgui.DockingSplit]:
        self._main_dock_space_id = initial_dock
        split_main_info = hello_imgui.DockingSplit(
            initial_dock_=self._main_dock_space_id,
            new_dock_=self._info_dock_space_id,
            direction_=imgui.Dir_.down,
            ratio_=0.1,
        )
        return [split_main_info]

    # ==================================================================================================================
    #                                  Utilities
    # ==================================================================================================================
    class _Utilities_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def _function_nodes(self) -> List[FunctionNodeGui]:
        return self._functions_graph_gui.function_nodes_gui

    def _shall_display_refresh_needed_label(self) -> bool:
        return self._functions_graph_gui.functions_graph.shall_display_refresh_needed_label()

    def _notify_if_dirty_functions(self) -> None:
        if not self._shall_display_refresh_needed_label():
            return

        def gui() -> None:
            imgui.text("Some functions need to be refreshed!")
            imgui.text("Click on the refresh button to recompute them.")

        fiat_osd.add_notification_gui("dirty", gui)

    # ==================================================================================================================
    #                                  Serialization
    # ==================================================================================================================
    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def _user_settings_filename(self) -> str:
        return hello_imgui.ini_settings_location(self.params.runner_params)[:-4] + ".fiat_user.json"

    def _graph_composition_filename(self) -> str:
        return hello_imgui.ini_settings_location(self.params.runner_params)[:-4] + ".fiat_graph.json"

    def _save_data(self, filename: str, save_type: _SaveType) -> None:
        has_extension = "." in filename
        if not has_extension:
            if save_type == _SaveType.GraphComposition:
                filename += ".fiat_graph.json"
            elif save_type == _SaveType.UserInputs:
                filename += ".fiat_user.json"

        json_data = {}
        if save_type == _SaveType.UserInputs:
            json_data = {
                "user_inputs": self._functions_graph_gui.save_user_inputs_to_json(),
                "gui_options": self._functions_graph_gui.save_gui_options_to_json(),
            }
        elif save_type == _SaveType.GraphComposition:
            json_data = self._functions_graph_gui.save_graph_composition_to_json()
        try:
            with open(filename, "w") as f:
                json_str = json.dumps(json_data, indent=4)
                f.write(json_str)
        except Exception as e:
            logging.error(f"FiatGui: Error saving state file {self._user_settings_filename()}: {e}")

    def _load_data(self, filename: str, whine_if_not_found: bool, save_type: _SaveType) -> bool:
        try:
            with open(filename, "r") as f:
                json_data = json.load(f)
        except json.JSONDecodeError as e:
            logging.warning(
                f"""
                JSONDecodeError when loading state file {self._user_settings_filename()}:
                (json.JSONDecodeError)
                ========================================
                {e}
                """
            )
            return False
        except FileNotFoundError:
            if whine_if_not_found:
                logging.warning(f"Could not find state file {self._user_settings_filename()}")
            return False
        try:
            if save_type == _SaveType.UserInputs:
                self._functions_graph_gui.load_user_inputs_from_json(json_data["user_inputs"])
                self._functions_graph_gui.load_gui_options_from_json(json_data["gui_options"])
            elif save_type == _SaveType.GraphComposition:

                def factor_function_from_name(name: str) -> Any:
                    return self._functions_collection_gui.functions_collection.factor_function_from_name(name)

                self._functions_graph_gui.load_graph_composition_from_json(json_data, factor_function_from_name)
        except Exception as e:
            logging.warning(
                f"""
                Error loading state file {self._user_settings_filename()}:
                (while invoking load_user_inputs_from_json: the nodes may have changed)
                ========================================
                Exception: {e}
                ========================================
                Traceback
                {traceback.format_exc()}
                """
            )
            # log traceback

            return False

        return True

    def _load_user_inputs_at_startup(self) -> None:
        self._load_data(self._user_settings_filename(), whine_if_not_found=False, save_type=_SaveType.UserInputs)

    def _load_user_inputs_during_execution(self, filename: str) -> None:
        success = self._load_data(filename, whine_if_not_found=True, save_type=_SaveType.UserInputs)
        if success:
            self._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=False)
            self._notify_if_dirty_functions()

    def _load_graph_composition_at_startup(self) -> None:
        self._load_data(
            self._graph_composition_filename(), whine_if_not_found=False, save_type=_SaveType.GraphComposition
        )

    def _load_graph_composition_during_execution(self, filename: str) -> None:
        success = self._load_data(filename, whine_if_not_found=True, save_type=_SaveType.GraphComposition)
        if success:
            self._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=False)

    def _save_user_inputs(self, filename: str) -> None:
        self._save_data(filename, _SaveType.UserInputs)

    def _save_graph_composition(self, filename: str) -> None:
        self._save_data(filename, _SaveType.GraphComposition)


def fiat_run_graph(
    functions_graph: FunctionsGraph,
    params: FiatGuiParams | None = None,
    app_name: str | None = None,
) -> None:
    from fiatlight.fiat_config.fiat_config_def import load_user_default_fiat_run_config

    # This will load the user default settings,
    # from a file named .fiat_run_config.json in the current directory or one of its parents.
    load_user_default_fiat_run_config()

    if _is_running_in_notebook():
        from fiatlight.fiat_runner.fiat_run_notebook import _fiat_run_graph_nb, NotebookRunnerParams

        if app_name is None:
            raise ValueError(
                "app_name must be specified when running in a notebook, so that the settings can be saved."
            )

        notebook_runner_params = NotebookRunnerParams()

        _fiat_run_graph_nb(
            functions_graph, params=params, app_name=app_name, notebook_runner_params=notebook_runner_params
        )
    else:
        fiat_gui = FiatGui(functions_graph, params=params, app_name=app_name)
        fiat_gui.run()


def fiat_run(
    fn: Function | FunctionWithGui,
    params: FiatGuiParams | None = None,
    app_name: str | None = None,
) -> None:
    functions_graph = FunctionsGraph.from_function(fn)
    fiat_run_graph(functions_graph, params=params, app_name=app_name)


def fiat_run_composition(
    composition: List[Function | FunctionWithGui],
    params: FiatGuiParams | None = None,
    app_name: str | None = None,
) -> None:
    """Runs a composition of functions in the Fiat GUI.
    - app_name: will be displayed in the window title, and used to save/load the user inputs and graph composition.
                if it is None, then the name of the calling module will be used.
                Note: inside a notebook, specifying app_name is mandatory, since the module name is not available.
    """
    functions_graph = FunctionsGraph.from_function_composition(composition)
    fiat_run_graph(functions_graph, params=params, app_name=app_name)


def run(
    fn: Function | FunctionWithGui | List[Function | FunctionWithGui] | FunctionsGraph,
    params: FiatGuiParams | None = None,
    app_name: str | None = None,
) -> None:
    """Runs a function, a composition of functions, or a functions graph in the Fiat GUI.

    - app_name: will be displayed in the window title, and used to save/load the user inputs and graph composition.
                if it is None, then the name of the calling module will be used.
                Note: inside a notebook, specifying app_name is mandatory, since the module name is not available.
    """
    if isinstance(fn, FunctionsGraph):
        fiat_run_graph(fn, params=params, app_name=app_name)
    elif isinstance(fn, list):
        fiat_run_composition(fn, params=params, app_name=app_name)
    elif isinstance(fn, FunctionWithGui):
        fiat_run(fn, params=params, app_name=app_name)
    else:
        fiat_run(fn, params=params, app_name=app_name)
