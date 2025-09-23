import traceback
from dataclasses import dataclass
from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui
from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui
from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_types.function_types import VoidFunction
from fiatlight.fiat_types.function_types import Function
from fiatlight.fiat_widgets import fiat_osd
from fiatlight.fiat_utils import functional_utils
from fiatlight.fiat_runner.functions_collection import FunctionCollectionGui
from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb
from fiatlight.fiat_config import get_fiat_config
from imgui_bundle import immapp, imgui, portable_file_dialogs as pfd, imgui_node_editor as ed
from typing import Any, Callable
from imgui_bundle import hello_imgui, ImVec2, immvision, imgui_md

import json
import logging
import pathlib
from typing import List, Tuple
from enum import Enum, auto

ImGuiTheme_ = hello_imgui.ImGuiTheme_


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


def is_running_in_notebook() -> bool:
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
    was_log_window_opened_on_first_log: bool = False

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
        if not self.was_log_window_opened_on_first_log:
            hello_imgui.get_runner_params().docking_params.dockable_window_of_name("Log").is_visible = True
            self.was_log_window_opened_on_first_log = True
        hello_imgui.log(level, msg)


def _init_logger() -> None:
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
_LAST_SCREENSHOT: ImageRgb | None = None


def get_last_screenshot() -> ImageRgb | None:
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
#                                  FiatRunParams
# ==================================================================================================================
@dataclass
class FiatRunParams:
    # members used to populate the runner_params
    app_name: str | None = None
    window_size: Tuple[int, int] | None = None
    enable_idling: bool = True
    theme: ImGuiTheme_ | None = None
    remember_theme: bool | None = None

    # FiatLight specific members
    customizable_graph: bool = False
    delete_settings: bool = False


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
    params: FiatRunParams

    _runner_params: hello_imgui.RunnerParams
    _functions_graph_gui: FunctionsGraphGui
    _show_inspector: bool = False

    save_dialog: pfd.save_file | None = None
    save_dialog_callback: Callable[[str], None] | None = None
    load_dialog: pfd.open_file | None = None
    load_dialog_callback: Callable[[str], None] | None = None

    _functions_collection_gui: FunctionCollectionGui

    _logo_texture: immvision.GlTexture

    # ==================================================================================================================
    #                                  Constructor
    # ==================================================================================================================
    def __init__(
        self,
        functions_graph: FunctionsGraph,
        params: FiatRunParams | None = None,
    ) -> None:
        if params is None:
            params = FiatRunParams()
        self.params = params
        self._prepare_runner_params()

        self.apply_fiat_style_graph()

        self._functions_graph_gui = FunctionsGraphGui(functions_graph)

        if self.params.customizable_graph:
            self._functions_graph_gui.can_edit_graph = True

        self._functions_collection_gui = FunctionCollectionGui()

        self._functions_collection_gui.on_add_function = lambda fn: self._functions_graph_gui.add_function_with_gui(fn)

        if self.params.delete_settings:
            self._del_user_settings()
        self.was_post_init_called = False

    def _prepare_runner_params(self) -> None:
        params = self.params
        runner_params = hello_imgui.RunnerParams()

        runner_params.app_window_params.window_geometry.size = params.window_size or (1600, 1000)
        runner_params.imgui_window_params.default_imgui_window_type = (
            hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
        )
        runner_params.app_window_params.restore_previous_geometry = True
        runner_params.imgui_window_params.show_status_bar = True
        runner_params.imgui_window_params.enable_viewports = True
        runner_params.fps_idling.enable_idling = params.enable_idling

        # Setup theme
        if params.theme is not None:
            runner_params.imgui_window_params.tweaked_theme.theme = params.theme
            runner_params.imgui_window_params.remember_theme = False
        else:
            runner_params.imgui_window_params.tweaked_theme.theme = hello_imgui.ImGuiTheme_.darcula_darker
        if params.remember_theme is not None:
            runner_params.imgui_window_params.remember_theme = params.remember_theme

        # Setup menus: we redefine the menus completely inside _show_menus
        runner_params.imgui_window_params.show_menu_bar = True
        runner_params.imgui_window_params.show_menu_view = False
        runner_params.imgui_window_params.show_menu_app = False
        runner_params.callbacks.show_menus = self._show_menus

        # window title from app_title or the name of the calling module
        if params.app_name is not None:
            runner_params.app_window_params.window_title = params.app_name
        else:
            runner_params.app_window_params.window_title = _main_python_module_name()

        if len(runner_params.ini_filename) == 0:
            runner_params.ini_filename = _ini_filename_from_app_name(runner_params.app_window_params.window_title)

        self._runner_params = runner_params

    @staticmethod
    def apply_fiat_style_graph() -> None:
        from fiatlight.fiat_config.fiat_style_def import AnyGuiWithDataSettings, FiatStrTruncationParams

        get_fiat_config().style.any_gui_with_data_settings = AnyGuiWithDataSettings.default_in_function_graph()
        get_fiat_config().style.str_truncation = FiatStrTruncationParams.default_in_function_graph()

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
        _init_logger()

    def _before_exit(self) -> None:
        self._store_final_app_window_screenshot()
        self._functions_graph_gui.on_exit()
        if self.params.customizable_graph:
            self._save_graph_composition(self._graph_composition_filename())
        self._save_user_inputs(self._user_settings_filename())

    def _pre_new_frame(self) -> None:
        _ENQUEUED_CALLBACKS.run_pre_frame_callbacks()
        get_fiat_config().style.update_colors_from_imgui_colors()

    def run(self) -> None:
        self._runner_params.docking_params.docking_splits += self._docking_splits()
        self._runner_params.docking_params.dockable_windows += self._dockable_windows()

        self._runner_params.callbacks.before_exit = functional_utils.sequence_void_functions(
            self._before_exit,
            self._runner_params.callbacks.before_exit,
        )

        # We do not call self.post_init here, because it is preferable to call it once an imgui window
        # is available (otherwise we might get seg faults inside imgui when the user incorrectly
        # performs imgui calls in non GUI functions)
        # Instead self.post_init is called once in the first frame, by self._panel_graph
        #
        # self.params.runner_params.callbacks.post_init = functional_utils.sequence_void_functions(
        #     self._post_init, self.params.runner_params.callbacks.post_init
        # )

        self._runner_params.callbacks.pre_new_frame = self._pre_new_frame
        self._runner_params.callbacks.after_swap = self._post_gui_after_swap
        self._runner_params.callbacks.before_imgui_render = self._post_gui

        from fiatlight.fiat_widgets.fontawesome6_ctx_utils import _load_font_awesome_6  # noqa

        self._runner_params.callbacks.load_additional_fonts = functional_utils.sequence_void_functions(
            hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons, _load_font_awesome_6
        )

        # top_toolbar_options = hello_imgui.EdgeToolbarOptions(size_em=2.5, window_bg=ImVec4(0.3, 0.3, 0.3, 1.0))
        # self.params.runner_params.callbacks.add_edge_toolbar(
        #     edge_toolbar_type=hello_imgui.EdgeToolbarType.top,
        #     gui_function=lambda: self._top_toolbar(),
        #     options=top_toolbar_options,
        # )

        self._runner_params.callbacks.post_render_dockable_windows = self._heartbeat_post_render_dockable_windows

        addons = immapp.AddOnsParams()
        addons.with_node_editor = True
        addons.with_node_editor_config = ed.Config()
        addons.with_node_editor_config.force_window_content_width_to_node_width = True
        addons.with_markdown = True
        addons.with_implot = True

        immapp.run(self._runner_params, addons)

    def _store_final_app_window_screenshot(self) -> None:
        global _LAST_SCREENSHOT
        last_hello_imgui_image = hello_imgui.final_app_window_screenshot()
        nodes_boundings = self._functions_graph_gui._get_node_screenshot_boundings()  # noqa

        # Fix the boundings to be inside the image
        if nodes_boundings.min.x < 0:
            nodes_boundings.min.x = 0
        if nodes_boundings.min.y < 0:
            nodes_boundings.min.y = 0
        if nodes_boundings.max.x > last_hello_imgui_image.shape[1]:
            nodes_boundings.max.x = last_hello_imgui_image.shape[1]
        if nodes_boundings.max.y > last_hello_imgui_image.shape[0]:
            nodes_boundings.max.y = last_hello_imgui_image.shape[0]

        last_nodes_image = last_hello_imgui_image[
            int(nodes_boundings.min.y) : int(nodes_boundings.max.y),
            int(nodes_boundings.min.x) : int(nodes_boundings.max.x),
        ]
        _LAST_SCREENSHOT = last_nodes_image  # type: ignore

    def _heartbeat_post_render_dockable_windows(self) -> None:
        fiat_osd.render_all_osd()  # noqa
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
            self._runner_params.fps_idling.enable_idling = False

    # ==================================================================================================================
    #                                  GUI
    # ==================================================================================================================
    class _Gui_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def _show_menus(self) -> None:
        if not self.was_post_init_called:
            # it is preferable to call post_init once an imgui window is available
            # (otherwise we might get seg faults inside imgui when the user incorrectly performs imgui
            # calls in non GUI functions)
            self._post_init()
            self.was_post_init_called = True

        if imgui.begin_menu("File"):
            if imgui.menu_item_simple("Load user inputs"):
                self.load_dialog = pfd.open_file(title="Load user inputs")
                self.load_dialog_callback = self._load_user_inputs_during_execution
            if imgui.menu_item_simple("Save user inputs"):
                self.save_dialog = pfd.save_file(title="Save user inputs")
                self.save_dialog_callback = self._save_user_inputs

            if self.params.customizable_graph:
                imgui.separator()
                if imgui.menu_item_simple("Load graph definition"):
                    self.load_dialog = pfd.open_file(title="Load graph definition")
                    self.load_dialog_callback = self._load_graph_composition_during_execution

                if imgui.menu_item_simple("Save graph definition"):
                    self.save_dialog = pfd.save_file(title="Save graph definition")
                    self.save_dialog_callback = self._save_graph_composition

            imgui.separator()
            if imgui.menu_item_simple("Quit"):
                hello_imgui.get_runner_params().app_shall_exit = True

            imgui.end_menu()

        if imgui.begin_menu("Graph"):
            if imgui.menu_item_simple("Auto-Layout graph"):
                self._functions_graph_gui.shall_layout_graph = True
            imgui.end_menu()

        hello_imgui.show_view_menu(self._runner_params)

    def _show_help_and_logo_tooltip_window(self) -> None:
        def _read_logo_texture() -> None:
            if not hasattr(self, "_logo_texture"):
                from fiatlight.fiat_kits.fiat_image.imread_rgb import imread_rgb

                from fiatlight import fiat_assets_dir

                logo_path = fiat_assets_dir() + "/logo/logo_fiatlight.jpg"
                logo_image = imread_rgb(logo_path)
                self._logo_texture = immvision.GlTexture(logo_image)

        _read_logo_texture()
        from fiatlight.fiat_widgets.permanent_tooltip_window import compute_corner_position_from_window, CornerPosition

        logo_ratio = 600.0 / 800.0
        logo_height_em = 4.0
        logo_size = hello_imgui.em_to_vec2(logo_height_em * logo_ratio, logo_height_em)
        logo_pos = compute_corner_position_from_window(
            logo_size,
            padding_em=ImVec2(0.7, 2.1),
            position=CornerPosition.TOP_RIGHT,
        )
        logo_rect = imgui.internal.ImRect(logo_pos, logo_pos + logo_size)
        alpha = 0.5
        is_hovering = imgui.is_mouse_hovering_rect(logo_rect.min, logo_rect.max)
        if is_hovering:
            alpha = 1.0
        col = imgui.IM_COL32(255, 255, 255, int(255 * alpha))
        imgui.get_window_draw_list().add_image(
            imgui.ImTextureRef(self._logo_texture.texture_id), logo_pos, logo_pos + logo_size, col=col
        )
        if is_hovering:
            if imgui.begin_tooltip():
                logo_height_em_big = 16.0
                logo_size_big = hello_imgui.em_to_vec2(logo_height_em_big * logo_ratio, logo_height_em_big)
                imgui.image(imgui.ImTextureRef(self._logo_texture.texture_id), logo_size_big)
                imgui_md.render_unindented(
                    """
                    * Use the mouse wheel to zoom in and out in the graph
                    * Use the right mouse button to move the graph
                """
                )
                imgui.end_tooltip()

    def _draw_functions_graph(self) -> None:
        if imgui.get_frame_count() >= 3:
            # the window size is not available on the first frames,
            # and the node editor uses it to compute the initial position of the nodes
            # window_size = imgui.get_window_size()
            any_change = self._functions_graph_gui.draw()
            if any_change:
                self._notify_if_dirty_functions()

        self._show_help_and_logo_tooltip_window()

    def _post_gui(self) -> None:
        # We focus the functions graph window after a few frames,
        # because the functions' dockable focused windows are created in the first few frames and may
        # have taken the focus
        if imgui.get_frame_count() == 7:
            if len(self._functions_graph_gui.function_nodes_gui) > 1:
                hello_imgui.get_runner_params().docking_params.focus_dockable_window("Functions Graph")

        for fn in self._functions_graph_gui.function_nodes_gui:
            fn.focused_function_draw_window()

    def _post_gui_after_swap(self) -> None:
        _ENQUEUED_CALLBACKS.run_post_frame_callbacks()
        if self._functions_graph_gui.did_any_focused_window_change_something():
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

    def _docking_splits(self) -> List[hello_imgui.DockingSplit]:
        split_main_info = hello_imgui.DockingSplit(
            initial_dock_="MainDockSpace",
            new_dock_="log_dock",
            direction_=imgui.Dir.down,
            ratio_=0.1,
        )
        return [split_main_info]

    def _dockable_windows(self) -> List[hello_imgui.DockableWindow]:
        main_window = hello_imgui.DockableWindow(
            label_="Functions Graph",
            dock_space_name_="MainDockSpace",
            gui_function_=lambda: self._draw_functions_graph(),
        )
        image_inspector = hello_imgui.DockableWindow(
            label_="Image Inspector",
            dock_space_name_="MainDockSpace",
            gui_function_=lambda: immvision.inspector_show(),
            is_visible_=False,
        )
        logger_window = hello_imgui.DockableWindow(
            label_="Log",
            dock_space_name_="log_dock",
            gui_function_=lambda: hello_imgui.log_gui(),
            is_visible_=False,
        )
        r = [main_window, image_inspector, logger_window]
        return r

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

    def _del_user_settings(self) -> None:
        files = [
            self._user_settings_filename(),
            self._graph_composition_filename(),
            self._node_settings_filename(),
            hello_imgui.ini_settings_location(self._runner_params),
        ]
        for file in files:
            path = pathlib.Path(file)
            if path.exists():
                path.unlink()

    def _node_settings_filename(self) -> str:
        return hello_imgui.ini_settings_location(self._runner_params)[:-4] + ".node_editor.json"

    def _user_settings_filename(self) -> str:
        return hello_imgui.ini_settings_location(self._runner_params)[:-4] + ".fiat_user.json"

    def _graph_composition_filename(self) -> str:
        return hello_imgui.ini_settings_location(self._runner_params)[:-4] + ".fiat_graph.json"

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


def _fiat_run_graph(
    functions_graph: FunctionsGraph,
    params: FiatRunParams,
) -> None:
    if is_running_in_notebook():
        from fiatlight.fiat_runner.fiat_run_notebook import _fiat_run_graph_nb, NotebookRunnerParams

        if params.app_name is None:
            raise ValueError(
                "app_name must be specified when running in a notebook, so that the settings can be saved."
            )

        notebook_runner_params = NotebookRunnerParams()

        _fiat_run_graph_nb(
            functions_graph,
            params=params,
            notebook_runner_params=notebook_runner_params,
        )
    else:
        fiat_gui = FiatGui(
            functions_graph,
            params=params,
        )
        fiat_gui.run()


def _fiat_run_function(
    fn: Function | FunctionWithGui,
    params: FiatRunParams,
) -> None:
    functions_graph = FunctionsGraph.from_function(fn)
    _fiat_run_graph(
        functions_graph,
        params=params,
    )


def _fiat_run_composition(
    composition: List[Function | FunctionWithGui],
    params: FiatRunParams,
) -> None:
    functions_graph = FunctionsGraph.from_function_composition(composition)
    _fiat_run_graph(
        functions_graph,
        params=params,
    )


def run(
    fn: Function | FunctionWithGui | List[Function | FunctionWithGui] | FunctionsGraph,
    params: FiatRunParams | None = None,
    app_name: str | None = None,
) -> None:
    """Runs a function, a composition of functions, or a functions graph in the Fiat GUI.

    - app_name: will be displayed in the window title, and used to save/load the user inputs and graph composition.
                if it is None, then the name of the calling module will be used.
                Note: inside a notebook, specifying app_name is mandatory, since the module name is not available.
    - theme: the theme to use. If None, the default theme will be used.
    - remember_theme: if True, the user selected theme will be saved in the settings file, and restored at the next run.
                      (this will bypass the theme parameter)
    """
    if params is None:
        params = FiatRunParams()
    if app_name is not None:
        params.app_name = app_name

    if isinstance(fn, FunctionsGraph):
        _fiat_run_graph(
            fn,
            params=params,
        )
    elif isinstance(fn, list):
        _fiat_run_composition(
            fn,
            params=params,
        )
    else:
        _fiat_run_function(
            fn,
            params=params,
        )
