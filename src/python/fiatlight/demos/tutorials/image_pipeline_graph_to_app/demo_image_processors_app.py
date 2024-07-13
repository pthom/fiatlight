"""An example application where you can display a camera image, apply a variety of image effects onto it.

This is an advanced example usage of Fiatlight, inside a full-fledged standard application: we will
not be using a FunctionGraph here, but we will use the GUI provided by Fiatlight
and Dear ImGui / Hello ImGui.

This example is heavily documented and tries to show how the main interesting features
of Fiatlight and Dear ImGui / Hello ImGui.

It is voluntarily split into several small classes to show an example on how to structure
an application with Fiatlight.

This example shows sophisticated usage features:
    Related to Fiatlight:
        - How to reuse the sophisticated GUI provided by Fiatlight in a standard application
        - How to display part of GUI in detachable windows
        - How to save and load the state of the application
        - How to save and load the GUI options of the application
        - How to use the fonts and icons provided by Fiatlight
    Related to ImGui and Hello ImGui:
        - How to create a complex GUI with multiple dockable windows
        - How to use a custom theme
        - How to create a custom toolbar
        - How to align the GUI elements with springs and Horizontal/Vertical layouts
"""

import fiatlight as fl
from fiatlight.demos.tutorials.image_pipeline_graph_to_app.image_processors import ImageEffect
from fiatlight.fiat_kits.fiat_image.camera_image_provider import CameraParams, CameraImageProvider
from imgui_bundle import imgui, immapp, immvision, hello_imgui, ImVec4
from pydantic import BaseModel
import json


def get_this_module_path() -> str:
    """Get the path of the current module, without the extension
    This is only used to save the settings beside this Python file.
    """
    import os
    import sys

    script_path = os.path.abspath(sys.argv[0])
    script_path_no_ext = os.path.splitext(script_path)[0]
    return script_path_no_ext


THIS_SCRIPT_PATH = get_this_module_path()
SETTINGS_FOLDER = THIS_SCRIPT_PATH + "_settings/"


@fl.base_model_with_gui_registration()
class AppState(BaseModel):
    """Our AppState is grouped into a BaseModel which is registered with the GUI.
    This offers several advantages:
       - easy serialization/deserialization of the state data
       - easy GUI creation
       - easy serialization/deserialization of the GUI options
    """

    camera_params: CameraParams = CameraParams()
    effects: ImageEffect = ImageEffect()


class AppResources:
    """AppResources is a class that contains the resources used by the application (sockets, files, IO devices, ...)
    In our case we have only one resource: the camera provider (which provides images from a camera).
    """

    camera_provider: CameraImageProvider

    def __init__(self) -> None:
        self.camera_provider = CameraImageProvider()


class Application:
    """The main application class
    It is responsible for:
        - creating the GUI for the application state
        - creating the resources used by the application
        - displaying the GUI (with three parts: camera image, image with effects, and camera parameters)
        - saving and loading the state of the application
        - saving and loading the GUI options of the application
    """

    # _params_gui is a data with GUI that contains:
    # - the application state (AppState), inside self._params_gui.value
    # - the GUI to edit the application state
    _params_gui: fl.AnyDataWithGui[AppState]

    # Those are the resources used by the application
    resources: AppResources

    def __init__(self) -> None:
        # Create the Gui for the application state. It will initially contain a default AppState.
        app_state = AppState()
        self._params_gui = fl.to_data_with_gui(app_state)  # noqa

        # Create the camera provider
        self.resources = AppResources()

    def gui_params(self) -> None:
        _params_changed = self._params_gui.gui_edit()

        if _params_changed:
            self.resources.camera_provider.apply_params(self._app_state().camera_params)

        # button start/stop camera
        started = self.resources.camera_provider.started()
        if started:
            if imgui.button("Stop Camera"):
                self.resources.camera_provider.stop()
        else:
            if imgui.button("Start Camera"):
                self.resources.camera_provider.start()

        # Render the detachable windows that the user may have opened
        fl.fiat_widgets.fiat_osd.render_all_osd()

    def gui_camera(self) -> None:
        # Display the camera image
        img = self.resources.camera_provider.get_image()
        if img is not None:
            # Note: by using immvision.image(), we could have more features (zoom, pan, pixel info, ...)
            image_width_pixels = int(hello_imgui.em_size(30))  # Fixed image size (in pixels, calculated from em size)
            immvision.image_display("Camera", img, refresh_image=True, image_display_size=(image_width_pixels, 0))

    def gui_image_with_effects(self) -> None:
        # Apply the effects to the camera image
        img = self.resources.camera_provider.get_image()
        if img is not None:
            img = self._app_state().effects.process(img)
            image_width_pixels = int(hello_imgui.em_size(30))  # Fixed image size (in pixels, calculated from em size)
            immvision.image_display("Effects", img, refresh_image=True, image_display_size=(image_width_pixels, 0))

    def gui_top_toolbar(self) -> None:
        """Display the top toolbar of the application"""
        # import font and font context from fiatlight
        from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx

        # import imgui context from imgui_bundle (it is used to create the horizontal layout)
        from imgui_bundle import imgui_ctx

        # We specify sizes in em units, so that the GUI is adaptable to different screen DPIs
        button_size = hello_imgui.em_to_vec2(2.0, 2.0)
        with fontawesome_6_ctx():
            # Create a horizontal layout
            with imgui_ctx.begin_horizontal("TopToolbar", imgui.get_window_size()):
                # A spring extends to fill the available space
                imgui.spring()
                # Display the start/stop camera button
                # This button will be centered (since there is one spring before, and one after)
                if self.resources.camera_provider.started():
                    # Use the fontawesome icon for the stop button
                    if imgui.button(icons_fontawesome_6.ICON_FA_STOP, button_size):
                        self.resources.camera_provider.stop()
                else:
                    if imgui.button(icons_fontawesome_6.ICON_FA_CAMERA, button_size):
                        self.resources.camera_provider.start()
                imgui.spring()
                # Display the power off button, which will be placed on the right
                if imgui.button(icons_fontawesome_6.ICON_FA_POWER_OFF, button_size):
                    hello_imgui.get_runner_params().app_shall_exit = True

    def save_state_and_gui_options(self) -> None:
        self._save_state()
        self._save_gui_options()

    def load_state_and_gui_options(self) -> None:
        self._load_state()
        self._load_gui_options()

    def _app_state(self) -> AppState:
        assert isinstance(self._params_gui.value, AppState)
        return self._params_gui.value

    def _state_filename(self) -> str:
        r = SETTINGS_FOLDER + "/app_state.json"
        return r

    def _gui_options_filename(self) -> str:
        return SETTINGS_FOLDER + "/gui_options.json"

    def _save_state(self) -> None:
        filename = self._state_filename()
        as_dict = self._params_gui.call_save_to_dict(self._params_gui.value)
        json.dump(as_dict, open(filename, "w"), indent=4)

    def _load_state(self) -> None:
        filename = self._state_filename()
        try:
            as_dict = json.load(open(filename, "r"))
            self._params_gui.value = self._params_gui.call_load_from_dict(as_dict)
        except FileNotFoundError:
            pass

    def _save_gui_options(self) -> None:
        filename = self._gui_options_filename()
        as_dict = self._params_gui.call_save_gui_options_to_json()
        json.dump(as_dict, open(filename, "w"), indent=4)

    def _load_gui_options(self) -> None:
        filename = self._gui_options_filename()
        try:
            as_dict = json.load(open(filename, "r"))
            self._params_gui.call_load_gui_options_from_json(as_dict)
        except FileNotFoundError:
            pass


def remove_hello_imgui_settings(runner_params: hello_imgui.RunnerParams) -> None:
    """If desired, remove the settings file of Hello ImGui, to start with a fresh state"""
    import os

    settings_file: str = hello_imgui.ini_settings_location(runner_params)
    if os.path.exists(settings_file):
        os.remove(settings_file)


def main() -> None:
    """Our main entry point for the application
    It will:
        - Create the application instance
        - Create an instance of Hello ImGui RunnerParams
          (where all the GUI settings of the application are stored)
        - Set the GUI settings of the application:
            - set the window settings (native window, ImGui window)
            - instantiate the Docking layout (layout and windows content)
            - theme
        - Add the callbacks to save and load the state of the application
        - run the application
    """
    app = Application()

    # Hello ImGui params (they hold the GUI settings of the application)
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Demo Image Processors App"

    # Standard ImGui window settings
    runner_params.imgui_window_params.show_status_bar = True
    runner_params.imgui_window_params.show_menu_bar = True

    # Theme
    runner_params.imgui_window_params.tweaked_theme.theme = hello_imgui.ImGuiTheme_.photoshop_style

    # Save and load the state of the application
    runner_params.callbacks.post_init = app.load_state_and_gui_options
    runner_params.callbacks.before_exit = app.save_state_and_gui_options

    # A. Application window settings
    # * Initial window size and restore previous geometry (from the previous run)
    runner_params.app_window_params.window_geometry.size = (1000, 900)
    runner_params.app_window_params.restore_previous_geometry = True
    # * Borderless window (this is optional, only for the demo)
    runner_params.app_window_params.borderless = True
    runner_params.app_window_params.borderless_movable = True
    runner_params.app_window_params.borderless_resizable = True
    runner_params.app_window_params.borderless_closable = True

    # B. ImGui window settings
    # * Use dockable windows
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )

    # C. Dockable window layout
    # We want this to create this Dockable spaces:
    #    ___________________________________________
    #    |         |                                |  # The Dockable Space "MainDockSpace" is provided automatically,
    #    | Cam     |    Camera Image                |  # The Camera Image will be placed in this space,
    #    | Params  |    (aka "MainDockSpace")       |  # after it was split into three parts with the code below.
    #    |   &     |________________________________|
    #    | Effects |                                |
    #    |         |     Image with Effect          |
    #    |         |                                |
    #    --------------------------------------------
    split_main_params = hello_imgui.DockingSplit()
    split_main_params.initial_dock = "MainDockSpace"
    split_main_params.new_dock = "CamParamsAndEffects"
    split_main_params.direction = imgui.Dir.left
    split_main_params.ratio = 0.4

    split_image_and_effect = hello_imgui.DockingSplit()
    split_image_and_effect.initial_dock = "MainDockSpace"
    split_image_and_effect.new_dock = "ImageWithEffect"
    split_image_and_effect.direction = imgui.Dir.down
    split_image_and_effect.ratio = 0.5

    runner_params.docking_params.docking_splits = [split_main_params, split_image_and_effect]

    # D. Dockable windows content
    # * The Camera Image
    camera_window = hello_imgui.DockableWindow()
    camera_window.label = "Camera"
    camera_window.dock_space_name = "MainDockSpace"
    camera_window.gui_function = app.gui_camera
    # * The Image with Effects
    effects_window = hello_imgui.DockableWindow()
    effects_window.label = "Effects"
    effects_window.dock_space_name = "ImageWithEffect"
    effects_window.gui_function = app.gui_image_with_effects
    # * The Params
    params_window = hello_imgui.DockableWindow()
    params_window.label = "Params"
    params_window.dock_space_name = "CamParamsAndEffects"
    params_window.gui_function = app.gui_params

    # D. Top toolbar (a custom toolbar at the top of the window)
    top_toolbar_options = hello_imgui.EdgeToolbarOptions()
    top_toolbar_options.size_em = 2.2
    top_toolbar_options.window_bg = ImVec4(0.8, 0.8, 0.8, 0.55)
    # top toolbar
    runner_params.callbacks.add_edge_toolbar(
        hello_imgui.EdgeToolbarType.top,
        app.gui_top_toolbar,
        top_toolbar_options,
    )

    runner_params.docking_params.dockable_windows = [camera_window, effects_window, params_window]

    # Hello ImGui settings location
    runner_params.ini_folder_type = hello_imgui.IniFolderType.absolute_path
    runner_params.ini_filename = SETTINGS_FOLDER + "/hello_imgui.ini"
    # If desired, remove the settings file of Hello ImGui, to start with a fresh state
    remove_hello_imgui_settings(runner_params)

    # Run the application
    immapp.run(runner_params)


if __name__ == "__main__":
    main()
