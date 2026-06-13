import traceback
from dataclasses import dataclass
from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui
from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui
from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_types.base_types import JsonDict
from fiatlight.fiat_types.function_types import VoidFunction
from fiatlight.fiat_types.function_types import Function
from fiatlight.fiat_widgets import fiat_osd
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import icons_fontawesome_6
from fiatlight.fiat_utils import functional_utils
from fiatlight.fiat_palette import FunctionPalette
from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb
from fiatlight.fiat_config import get_fiat_config
from imgui_bundle import immapp, imgui, portable_file_dialogs as pfd, imgui_node_editor as ed
from typing import Any, Callable
from imgui_bundle import hello_imgui, ImVec2, ImVec4, immvision, imgui_md

import json
import logging
import pathlib
from typing import List, Tuple

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
# Orange tint used for the log-alert status-bar indicator and notification.
_LOG_ALERT_COLOR = ImVec4(1.0, 0.6, 0.0, 1.0)


class HelloImGuiLogHandler(logging.Handler):
    # Number of warning/error records logged since the user last opened the Log
    # window (drives the status-bar indicator). Reset when the Log is opened.
    nb_new_alerts: int = 0
    # Short message of the latest warning/error not yet shown as a notification.
    # Consumed (set to None) by the GUI heartbeat, which creates the toast there
    # so that no imgui call happens inside emit() (which may run off-frame).
    pending_alert_message: str | None = None

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
        # Flag warnings/errors so the GUI can alert the user (status bar +
        # notification) instead of force-opening the Log window.
        if record.levelno >= logging.WARNING:
            self.nb_new_alerts += 1
            self.pending_alert_message = record.getMessage().strip().split("\n")[0]


def _init_logger() -> HelloImGuiLogHandler:
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

    return hello_imgui_log_handler


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
    top_most: bool = False

    # FiatLight specific members
    customizable_graph: bool = False
    delete_settings: bool = False


# ==================================================================================================================
#                                  FiatGui
# ==================================================================================================================
class FiatGui:
    # ==================================================================================================================
    #                                  Members
    # ==================================================================================================================
    params: FiatRunParams

    _runner_params: hello_imgui.RunnerParams
    _functions_graph_gui: FunctionsGraphGui
    _show_inspector: bool = False

    # Frames to wait after a (re)load before snapshotting the undo baseline, so
    # node positions (applied deferred inside ed.begin/end) have settled.
    _UNDO_BASELINE_DELAY_FRAMES = 8
    # Frames the graph must stay settled before a reconcile snapshot is taken.
    _UNDO_SETTLE_FRAMES = 4

    save_dialog: pfd.save_file | None = None
    save_dialog_callback: Callable[[str], None] | None = None
    load_dialog: pfd.open_file | None = None
    load_dialog_callback: Callable[[str], None] | None = None

    # Sticky cursor: the workspace path Save / autosave-on-exit write to.
    # Initialised to the per-app autosave path; Open / Save As reseat it,
    # and the value is persisted across launches via hello_imgui user prefs.
    _current_workspace_path: str

    # Key used with hello_imgui.save_user_pref / load_user_pref. The value
    # lives inside the per-app .ini file managed by HelloImGui, so deleting
    # the .ini (via FiatRunParams.delete_settings) wipes the cursor too.
    _USER_PREF_LAST_WORKSPACE = "fiat.last_workspace_path"

    _function_palette: FunctionPalette

    _logo_texture: imgui.ImTextureRef

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
        self._current_workspace_path = self._workspace_filename()

        self.apply_fiat_style_graph()

        self._function_palette = FunctionPalette()
        self._functions_graph_gui = FunctionsGraphGui(functions_graph, function_palette=self._function_palette)

        if self.params.customizable_graph:
            self._functions_graph_gui.can_edit_graph = True

        # Undo/redo: full-graph snapshots, captured when an edit/drag settles.
        from fiatlight.fiat_runner.undo_manager import UndoManager

        self._undo_manager = UndoManager(self._functions_graph_gui.save_workspace_to_json, self._restore_graph_snapshot)
        self._undo_baseline_pending = self._UNDO_BASELINE_DELAY_FRAMES
        self._undo_settle_frames = 0
        self._undo_prev_layout_sig: Tuple[Tuple[str, int, int], ...] = ()
        # The graph snapshot as of the last save (or load); drives the status-bar
        # "unsaved changes" marker.
        self._saved_workspace_json: JsonDict = {}
        self._workspace_dirty = False

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
        runner_params.app_window_params.top_most = params.top_most

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
        runner_params.callbacks.show_status = self._show_status_bar

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
        self._restore_cursor_from_user_pref()
        self._load_workspace_at_startup()
        self._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=False)
        self._notify_if_dirty_functions()
        self._disable_idling_if_any_live_function()
        self._log_handler = _init_logger()

    def _before_exit(self) -> None:
        self._store_final_app_window_screenshot()
        self._functions_graph_gui.on_exit()
        # Sticky cursor: save to wherever the user last opened from (or
        # explicitly Saved As). At startup that is the default autosave path.
        self._save_workspace(self._current_workspace_path)
        # Remember the cursor across runs. Stored via hello_imgui's user-pref
        # storage (lives inside the per-app .ini), so the next launch resumes
        # the exact same workspace file even after Save As to a custom path.
        hello_imgui.save_user_pref(self._USER_PREF_LAST_WORKSPACE, self._current_workspace_path)

    def _pre_new_frame(self) -> None:
        _ENQUEUED_CALLBACKS.run_pre_frame_callbacks()
        get_fiat_config().style.update_colors_from_imgui_colors()

    def _setup_runner(self) -> Tuple[hello_imgui.RunnerParams, immapp.AddOnsParams]:
        """Setup the runner params and addons. Returns (runner_params, addons) for use with immapp.run or run_async."""
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
        # Disable imgui-node-editor's own JSON autosave
        addons.with_node_editor_config.settings_file = ""
        addons.with_markdown = True
        addons.with_implot = True

        return self._runner_params, addons

    def run(self) -> None:
        runner_params, addons = self._setup_runner()
        immapp.run(runner_params, addons)

    async def run_async(self) -> None:
        """Run the FiatGui asynchronously. Use this for async workflows or notebook integration."""
        runner_params, addons = self._setup_runner()
        await immapp.run_async(runner_params, addons)

    def _store_final_app_window_screenshot(self) -> None:
        global _LAST_SCREENSHOT
        if len(self._functions_graph_gui.function_nodes_gui) == 0:
            _LAST_SCREENSHOT = None
            return
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
        self._notify_if_new_log_alert()
        fiat_osd.render_all_osd()  # noqa
        self._handle_file_dialogs()

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
            # New empties the in-memory topology, which only makes sense
            # in composer mode (where topology comes from the user, not
            # from code). Open is available in both modes: in composer
            # mode it rebuilds topology, in programmatic mode it overlays
            # parameter values and GUI options onto the code-defined graph
            # (matched by stable_id; see `rebuild_topology` plumbing).
            if self.params.customizable_graph:
                if imgui.menu_item_simple("New Workspace"):
                    self._menu_new_workspace()
            if imgui.menu_item_simple("Open Workspace…"):
                self._menu_open_workspace()
            if imgui.menu_item_simple("Save Workspace", "Ctrl+S"):
                self._menu_save_workspace()
            if imgui.menu_item_simple("Save Workspace As…"):
                self._menu_save_workspace_as()

            imgui.separator()
            if imgui.menu_item_simple("Fit Canvas"):
                ed.navigate_to_content()

            imgui.separator()
            if imgui.menu_item_simple("Quit"):
                hello_imgui.get_runner_params().app_shall_exit = True

            imgui.end_menu()

        if imgui.begin_menu("Edit"):
            if imgui.menu_item_simple("Undo", "Ctrl+Z", False, self._undo_manager.can_undo()):
                self._undo_manager.undo()
            if imgui.menu_item_simple("Redo", "Ctrl+Shift+Z", False, self._undo_manager.can_redo()):
                self._undo_manager.redo()
            imgui.end_menu()

        if imgui.begin_menu("Graph"):
            if imgui.menu_item_simple("Auto-Layout graph"):
                self._functions_graph_gui.shall_layout_graph = True
            imgui.end_menu()

        hello_imgui.show_view_menu(self._runner_params)

    def _menu_new_workspace(self) -> None:
        # Reset the sticky cursor too, so a New + Quit doesn't silently
        # overwrite the user's previously-saved-As file with an empty graph.
        # The next exit-save lands in the default per-app autosave path,
        # which is the closest equivalent we have to "Untitled".
        self._functions_graph_gui.clear()
        self._current_workspace_path = self._workspace_filename()
        self._request_undo_baseline()

    def _menu_open_workspace(self) -> None:
        self.load_dialog = pfd.open_file(title="Open Workspace")
        self.load_dialog_callback = self._load_workspace_during_execution

    def _menu_save_workspace(self) -> None:
        self._save_workspace(self._current_workspace_path)

    def _menu_save_workspace_as(self) -> None:
        self.save_dialog = pfd.save_file(title="Save Workspace As")
        self.save_dialog_callback = self._save_workspace_as

    def _show_help_and_logo_tooltip_window(self) -> None:
        def _read_logo_texture() -> None:
            if not hasattr(self, "_logo_texture"):
                from imgui_bundle import hello_imgui
                from fiatlight import fiat_assets_dir

                logo_path = fiat_assets_dir() + "/logo/logo_fiatlight.jpg"
                self._logo_texture = imgui.ImTextureRef(hello_imgui.im_texture_id_from_asset(logo_path))

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
        imgui.get_window_draw_list().add_image(self._logo_texture, logo_pos, logo_pos + logo_size, col=col)
        if is_hovering:
            if imgui.begin_tooltip():
                logo_height_em_big = 16.0
                logo_size_big = hello_imgui.em_to_vec2(logo_height_em_big * logo_ratio, logo_height_em_big)
                imgui.image(self._logo_texture, logo_size_big)
                imgui.dummy(hello_imgui.em_to_vec2(40, 0))
                imgui_md.render_unindented(
                    """
* Use the mouse wheel to zoom in and out in the graph
* Drag with the right mouse button to move the graph

### Mouse

| Input                                | Action |
|--------------------------------------|--------|
| Left click on background             | Clear selection |
| Left click on node or link           | Select that object (replaces selection) |
| `Ctrl` + left click                  | Toggle the clicked object in or out of the selection |
| Left drag on background              | Rubber-band select nodes |
| `Shift` + left drag on background    | Rubber-band select Group nodes |
| `Alt` + left drag on background      | Rubber-band select links |
| `Ctrl` + left drag (rubber band)     | Keep the previous selection while lassoing |
| Left drag on a node                  | Move the node (and members of any selected Group) |
| `Shift` + left drag on a node        | Move only the directly-selected nodes |
| Right drag                           | Pan the canvas |
| Right click                          | Open the context menu |
| Mouse wheel                          | Zoom in or out (smooth zoom controlled by `Config::EnableSmoothZoom`) |

### Keyboard

| Input                  | Action |
|------------------------|--------|
| `F` over a node, pin or Group | Center that object  |
| `F` with a non-empty selection| Center the selection bounds  |
| `F` over the empty background | Center all content |
| `Shift` + `F`                 | Same as `F`, but with zoom |

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
            # Runs in the "Functions Graph" window scope (after ed.end), so the
            # undo shortcuts use the focused route (yield Ctrl+Z to text inputs).
            self._handle_undo_redo()

        self._show_help_and_logo_tooltip_window()

    def _request_undo_baseline(self) -> None:
        """Re-snapshot the undo baseline (after New / Open), once positions settle."""
        self._undo_baseline_pending = self._UNDO_BASELINE_DELAY_FRAMES

    def _restore_graph_snapshot(self, snapshot: JsonDict) -> None:
        rebuild_topology = self.params.customizable_graph
        self._functions_graph_gui.load_workspace_from_json(
            snapshot, self._function_palette.factor_function_from_ref, rebuild_topology=rebuild_topology
        )
        self._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=False)

    def _handle_undo_redo(self) -> None:
        # Wait for positions to settle, then snapshot the baseline.
        if self._undo_baseline_pending > 0:
            self._undo_baseline_pending -= 1
            if self._undo_baseline_pending == 0:
                self._undo_manager.reset()
                self._undo_prev_layout_sig = self._functions_graph_gui.nodes_layout_signature()
                # Baseline == the on-disk state we just loaded -> clean.
                self._saved_workspace_json = self._undo_manager.current()
                self._workspace_dirty = False
            return

        # Shortcuts: focused route, so an active text input keeps its own Ctrl+Z.
        ctrl = imgui.Key.mod_ctrl.value
        shift = imgui.Key.mod_shift.value
        z = imgui.Key.z.value
        route = imgui.InputFlags_.route_focused.value
        if imgui.shortcut(ctrl | z, route):
            self._undo_manager.undo()
            self._update_workspace_dirty()
        if imgui.shortcut(ctrl | shift | z, route):
            self._undo_manager.redo()
            self._update_workspace_dirty()
        if imgui.shortcut(ctrl | imgui.Key.s.value, route):
            self._menu_save_workspace()

        # Reconcile only when the graph has settled (no active widget, positions
        # stable) so a continuous gesture becomes one undo step.
        layout_sig = self._functions_graph_gui.nodes_layout_signature()
        settled = (not imgui.is_any_item_active()) and (layout_sig == self._undo_prev_layout_sig)
        self._undo_prev_layout_sig = layout_sig
        if settled:
            self._undo_settle_frames += 1
            # `==` (not `>=`): serialize once when the graph crosses into
            # "settled", not on every idle frame. Every real change perturbs the
            # cheap settle signals (active-item / layout sig), so it re-settles
            # and snapshots exactly once per change.
            if self._undo_settle_frames == self._UNDO_SETTLE_FRAMES:
                if self._undo_manager.reconcile():
                    self._update_workspace_dirty()
        else:
            self._undo_settle_frames = 0

    def _update_workspace_dirty(self) -> None:
        self._workspace_dirty = self._undo_manager.current() != self._saved_workspace_json

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
        splits: List[hello_imgui.DockingSplit] = []
        splits.append(
            hello_imgui.DockingSplit(
                initial_dock_="MainDockSpace",
                new_dock_="log_dock",
                direction_=imgui.Dir.down,
                ratio_=0.1,
            )
        )
        return splits

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
        return [main_window, image_inspector, logger_window]

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

    def _open_log_window(self) -> None:
        self._runner_params.docking_params.dockable_window_of_name("Log").is_visible = True
        self._log_handler.nb_new_alerts = 0

    def _show_status_bar(self) -> None:
        """Status-bar content: the active workspace file (the one Save writes to),
        plus a discreet indicator when warnings/errors were logged."""
        # Active workspace file. Show a short name; full path on hover.
        # The default per-app path auto-saves on exit, so a "*" there would just
        # be noise — the marker is shown only for an explicitly named file.
        is_default = self._current_workspace_path == self._workspace_filename()
        name = pathlib.Path(self._current_workspace_path).name
        if name.endswith(".fiat_workspace.json"):
            name = name[: -len(".fiat_workspace.json")]
        marker = " *" if (self._workspace_dirty and not is_default) else ""
        imgui.text_disabled(f"{icons_fontawesome_6.ICON_FA_FILE} {name}{marker}")
        if imgui.is_item_hovered():
            lines = []
            if is_default:
                lines.append("Default workspace")
            lines.append(self._current_workspace_path)
            lines.append("Auto-saved on exit.")
            imgui.set_tooltip("\n".join(lines))

        if self._log_handler.nb_new_alerts > 0:
            imgui.same_line()
            imgui.text_disabled(" | ")
            imgui.same_line()
            n = self._log_handler.nb_new_alerts
            msg = f"{icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION} {n} new log message" + ("s" if n > 1 else "")
            imgui.text_colored(_LOG_ALERT_COLOR, msg)
            imgui.same_line()
            if imgui.small_button("Open Log"):
                self._open_log_window()

    def _notify_if_new_log_alert(self) -> None:
        message = self._log_handler.pending_alert_message
        if message is None:
            return
        self._log_handler.pending_alert_message = None

        def gui() -> None:
            imgui.text_colored(_LOG_ALERT_COLOR, f"{icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION}  Logged:")
            imgui.text_wrapped(message)

        fiat_osd.add_notification_gui("log_alert", gui)

    # ==================================================================================================================
    #                                  Serialization
    # ==================================================================================================================
    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
        pass

    def _del_user_settings(self) -> None:
        loc = hello_imgui.ini_settings_location(self._runner_params)
        assert loc is not None
        stem = loc[:-4]
        files = [
            self._workspace_filename(),
            # Legacy files from earlier fiatlight versions. Kept in the
            # cleanup list so reset-settings scrubs any leftover, including
            # the short-lived per-app session split (`.fiat_session.json`)
            # that was folded back into the workspace.
            stem + ".fiat_session.json",
            stem + ".fiat_user.json",
            stem + ".fiat_graph.json",
            stem + ".node_editor.json",
            loc,
        ]
        for file in files:
            path = pathlib.Path(file)
            if path.exists():
                path.unlink()

    def _workspace_filename(self) -> str:
        loc = hello_imgui.ini_settings_location(self._runner_params)
        assert loc is not None
        return loc[:-4] + ".fiat_workspace.json"

    def _save_workspace(self, filename: str) -> None:
        if "." not in filename:
            filename += ".fiat_workspace.json"
        try:
            json_data = self._functions_graph_gui.save_workspace_to_json()
        except Exception as e:
            logging.error(f"FiatGui: error building workspace JSON: {e}\n{traceback.format_exc()}")
            return
        try:
            with open(filename, "w") as f:
                json.dump(json_data, f, indent=4)
        except Exception as e:
            logging.error(f"FiatGui: error saving workspace to {filename}: {e}")
            return
        # What we just wrote is now the on-disk state -> clean.
        self._saved_workspace_json = json_data
        self._workspace_dirty = False

    def _load_workspace(self, filename: str, whine_if_not_found: bool) -> bool:
        try:
            with open(filename, "r") as f:
                json_data = json.load(f)
        except FileNotFoundError:
            if whine_if_not_found:
                logging.warning(f"FiatGui: workspace file not found: {filename}")
            return False
        except json.JSONDecodeError as e:
            logging.warning(f"FiatGui: workspace JSON decode error in {filename}: {e}")
            return False
        rebuild_topology = self.params.customizable_graph
        try:
            self._functions_graph_gui.load_workspace_from_json(
                json_data,
                self._function_palette.factor_function_from_ref,
                rebuild_topology=rebuild_topology,
            )
        except Exception as e:
            logging.warning(f"FiatGui: error loading workspace from {filename}: {e}\n{traceback.format_exc()}")
            return False
        return True

    def _load_workspace_at_startup(self) -> None:
        # `_current_workspace_path` was already reseated by
        # `_restore_cursor_from_user_pref` if the previous run left a valid
        # cursor; otherwise it is still the default per-app autosave path.
        self._load_workspace(self._current_workspace_path, whine_if_not_found=False)

    def _restore_cursor_from_user_pref(self) -> None:
        """Reseat `_current_workspace_path` from the user pref written on
        the previous exit. Falls back to the default path (and clears the
        pref) when the recorded file no longer exists or cannot be parsed."""
        try:
            stored = hello_imgui.load_user_pref(self._USER_PREF_LAST_WORKSPACE)
            if stored.endswith("\n"):
                stored = stored[:-1]
        except Exception as e:
            logging.warning(f"FiatGui: cannot read user pref {self._USER_PREF_LAST_WORKSPACE!r}: {e}")
            return
        if not stored:
            return
        if not pathlib.Path(stored).is_file():
            logging.info(
                f"FiatGui: stored workspace cursor {stored!r} no longer exists; " "falling back to default path."
            )
            hello_imgui.save_user_pref(self._USER_PREF_LAST_WORKSPACE, "")
            return
        self._current_workspace_path = stored

    def _load_workspace_during_execution(self, filename: str) -> None:
        success = self._load_workspace(filename, whine_if_not_found=True)
        if not success:
            return
        self._current_workspace_path = filename
        self._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=False)
        self._notify_if_dirty_functions()
        self._request_undo_baseline()

    def _save_workspace_as(self, filename: str) -> None:
        if "." not in pathlib.Path(filename).name:
            filename += ".fiat_workspace.json"
        self._save_workspace(filename)
        self._current_workspace_path = filename


def _fiat_run_graph(
    functions_graph: FunctionsGraph,
    params: FiatRunParams,
) -> None:
    if is_running_in_notebook():
        from fiatlight.fiat_runner.fiat_run_notebook import _fiat_nb_run_graph_and_save_screenshot, NotebookRunnerParams

        if params.app_name is None:
            raise ValueError(
                "app_name must be specified when running in a notebook, so that the settings can be saved."
            )

        notebook_runner_params = NotebookRunnerParams()

        _fiat_nb_run_graph_and_save_screenshot(
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


def run_graph_composer(
    functions: List[Function],
    initial_graph: FunctionsGraph | None = None,
    params: FiatRunParams | None = None,
    app_name: str | None = None,
    top_most: bool = False,
) -> None:
    """Run the Fiat GUI as a graph composer: a function palette (built from
    `functions`) that the user can drag into a live, editable function graph.

    - functions: list of functions exposed in the palette. Each must carry
                 `fiat_tags` (set via `@fl.with_fiat_attributes(...)` or
                 `fl.add_fiat_attributes(...)`).
    - initial_graph: optional starter wiring. If None, the composer starts
                     with an empty graph.
    - params, app_name, top_most: same meaning as in `run()`.
    """
    if params is None:
        params = FiatRunParams()
    if app_name is not None:
        params.app_name = app_name
    if top_most:
        params.top_most = top_most
    params.customizable_graph = True

    graph = initial_graph if initial_graph is not None else FunctionsGraph.create_empty()
    fiat_gui = FiatGui(graph, params=params)
    for fn in functions:
        fiat_gui._function_palette.add_function(fn)
    fiat_gui.run()


def studio(
    functions: List[Function] | None = None,
    params: FiatRunParams | None = None,
    app_name: str | None = None,
    top_most: bool = False,
) -> None:
    """Open the Fiatlight studio: an interactive node composer.

    Launches the graph composer with a palette of all available built-in node
    packs (image / math / text — the image pack needs opencv; packs whose
    dependencies are missing are skipped). Drag nodes onto the canvas to build a
    live function graph. Pass `functions` to add your own nodes to the palette.
    """
    from fiatlight.fiat_kits.node_packs import default_nodes

    palette = default_nodes()
    if functions:
        palette = palette + list(functions)
    run_graph_composer(
        functions=palette,
        params=params,
        app_name=app_name if app_name is not None else "fiatlight studio",
        top_most=top_most,
    )


def run(
    fn: Function | FunctionWithGui | List[Function | FunctionWithGui] | FunctionsGraph,
    params: FiatRunParams | None = None,
    app_name: str | None = None,
    top_most: bool = False,
) -> None:
    """Runs a function, a composition of functions, or a functions graph in the Fiat GUI.

    - app_name: will be displayed in the window title, and used to save/load the user inputs and graph composition.
                if it is None, then the name of the calling module will be used.
                Note: inside a notebook, specifying app_name is mandatory, since the module name is not available.
    - top_most: if True, the window will stay on top of other windows (useful in notebooks). Default: False.
    - theme: the theme to use. If None, the default theme will be used.
    - remember_theme: if True, the user selected theme will be saved in the settings file, and restored at the next run.
                      (this will bypass the theme parameter)
    """
    if params is None:
        params = FiatRunParams()
    if app_name is not None:
        params.app_name = app_name
    if top_most:
        params.top_most = top_most

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


# ==================================================================================================================
#                                  Async run functions
# ==================================================================================================================
async def _fiat_run_graph_async(
    functions_graph: FunctionsGraph,
    params: FiatRunParams,
) -> None:
    fiat_gui = FiatGui(
        functions_graph,
        params=params,
    )
    await fiat_gui.run_async()


async def _fiat_run_function_async(
    fn: Function | FunctionWithGui,
    params: FiatRunParams,
) -> None:
    functions_graph = FunctionsGraph.from_function(fn)
    await _fiat_run_graph_async(
        functions_graph,
        params=params,
    )


async def _fiat_run_composition_async(
    composition: List[Function | FunctionWithGui],
    params: FiatRunParams,
) -> None:
    functions_graph = FunctionsGraph.from_function_composition(composition)
    await _fiat_run_graph_async(
        functions_graph,
        params=params,
    )


async def run_async(
    fn: Function | FunctionWithGui | List[Function | FunctionWithGui] | FunctionsGraph,
    params: FiatRunParams | None = None,
    app_name: str | None = None,
    top_most: bool = False,
) -> None:
    """Runs a function, a composition of functions, or a functions graph in the Fiat GUI asynchronously.

    This is the async version of `run()`. Use this for async workflows or notebook integration.

    - app_name: will be displayed in the window title, and used to save/load the user inputs and graph composition.
                if it is None, then the name of the calling module will be used.
                Note: inside a notebook, specifying app_name is mandatory, since the module name is not available.
    - top_most: if True, the window will stay on top of other windows (useful in notebooks). Default: False.
    - theme: the theme to use. If None, the default theme will be used.
    - remember_theme: if True, the user selected theme will be saved in the settings file, and restored at the next run.
                      (this will bypass the theme parameter)
    """
    if params is None:
        params = FiatRunParams()
    if app_name is not None:
        params.app_name = app_name
    if top_most:
        params.top_most = top_most

    if isinstance(fn, FunctionsGraph):
        await _fiat_run_graph_async(
            fn,
            params=params,
        )
    elif isinstance(fn, list):
        await _fiat_run_composition_async(
            fn,
            params=params,
        )
    else:
        await _fiat_run_function_async(
            fn,
            params=params,
        )
