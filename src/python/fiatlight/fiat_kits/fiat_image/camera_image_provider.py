import copy
import logging
import cv2
import os  # noqa
from pydantic import BaseModel

from fiatlight.fiat_togui.gui_registry import base_model_with_gui_registration
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_kits.fiat_image import ImageRgb
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_utils import add_fiat_attributes
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from enum import Enum
from imgui_bundle import imgui, imgui_ctx, hello_imgui
from typing import Optional

# hack, used when building documentation: we replace the camera image with a static image or video
_HACK_IMAGE: ImageRgb | None = None
_HACK_MOVIE: str | None = None

# _HACK_IMAGE: ImageRgb = fl.imread_rgb(os.path.dirname(__file__) + "/paris.jpg")  # type: ignore
# _HACK_MOVIE = "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/priv_assets/videos_demos/Sintel.2010.720p.mkv"  # noqa


def _raise_if_incorrect_windows_opencv_capture_env_config() -> None:
    """On  windows, capture startup can be very slow, unless an environment variable is set
    See https://github.com/opencv/opencv/issues/17687
    """
    import platform

    if platform.system() != "Windows":
        return
    import os

    message = """
        On  windows, capture startup ca be very slow, unless an environment variable is set.
        Please set the environment variable OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS to 0
    """
    if "OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS" not in os.environ:
        raise ValueError(message)
    if os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] != "0":
        raise ValueError(message)


class CameraResolution(Enum):
    """Some typical camera resolutions"""

    HD_1280_720 = [1280, 720]
    FULL_HD_1920_1080 = [1920, 1080]
    VGA_640_480 = [640, 480]
    QVGA_320_240 = [320, 240]


add_fiat_attributes(
    CameraResolution,
    HD_1280_720__label="1280x720",
    HD_1280_720__tooltip="High Definition",
    #
    FULL_HD_1920_1080__label="1920x1080",
    FULL_HD_1920_1080__tooltip="Full HD",
    #
    VGA_640_480__label="640x480",
    VGA_640_480__tooltip="VGA",
    #
    QVGA_320_240__label="320x240",
)


@base_model_with_gui_registration(device_number__range=(0, 5))
class CameraParams(BaseModel):
    """Parameters for the camera image provider"""

    device_number: int = 0
    camera_resolution: CameraResolution = CameraResolution.VGA_640_480


class CameraImageProvider:
    """A class to provide images from a camera"""

    camera_params: CameraParams
    previous_camera_params: Optional[CameraParams] = None
    cv_cap: cv2.VideoCapture | None = None

    def __init__(self, params: Optional[CameraParams] = None):
        if params is None:
            params = CameraParams()
        self.camera_params = params

    def get_image(self) -> ImageRgb | None:
        if _HACK_IMAGE is not None:
            return _HACK_IMAGE
        if self.cv_cap is None:
            return None
        ret, frame = self.cv_cap.read()
        if frame is None:
            return None
        if frame.shape[0] == 0 or frame.shape[1] == 0:
            return None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame_rgb  # type: ignore

    def apply_params(self, params: CameraParams) -> None:
        if self.previous_camera_params is not None and params == self.previous_camera_params:
            return
        if self.cv_cap is None:
            self.camera_params = params
            return
        self.previous_camera_params = copy.deepcopy(self.camera_params)
        self.camera_params = params
        self.stop()
        self.start()

    def start(self) -> None:
        logging.info(f"CameraImageProvider start: {self.camera_params}")
        self.cv_cap = cv2.VideoCapture()
        if _HACK_MOVIE is not None and os.path.exists(_HACK_MOVIE):
            self.cv_cap.open(_HACK_MOVIE)
        else:
            _raise_if_incorrect_windows_opencv_capture_env_config()
            self.cv_cap.open(self.camera_params.device_number)
        frame_width_set = self.cv_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_params.camera_resolution.value[0])
        frame_height_set = self.cv_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_params.camera_resolution.value[1])

        if not frame_width_set or not frame_height_set:
            logging.warning("This camera does not support setting frame width and height")

        self.previous_camera_params = copy.deepcopy(self.camera_params)

    def stop(self) -> None:
        logging.info("CameraImageProvider stop")
        if self.cv_cap is None:
            return
        self.cv_cap.release()
        self.cv_cap = None

    def started(self) -> bool:
        return self.cv_cap is not None


class CameraImageProviderGui(FunctionWithGui):
    """A Gui for the camera image provider"""

    _camera_provider: CameraImageProvider
    _camera_params_gui: AnyDataWithGui[CameraParams]

    def __init__(self) -> None:
        super().__init__(self.f, "CameraImageProviderGui")

        from fiatlight.fiat_togui import to_data_with_gui

        self._camera_provider = CameraImageProvider()
        self._camera_params_gui = to_data_with_gui(self._camera_provider.camera_params)
        self._camera_params_gui.label = "Camera Params"

        self.internal_state_gui = self._internal_state_gui
        self.save_internal_gui_options_to_json = self._save_internal_gui_options_to_json
        self.load_internal_gui_options_from_json = self._load_internal_gui_options_from_json

        # A flag for fiatlight to set this as a live function
        self.invoke_always_dirty = True

    def f(self) -> ImageRgb | None:
        return self._camera_provider.get_image()

    def _save_internal_gui_options_to_json(self) -> JsonDict:
        r = self._camera_provider.camera_params.model_dump(mode="json")
        return r

    def _load_internal_gui_options_from_json(self, json_dict: JsonDict) -> None:
        camera_params = CameraParams.model_validate(json_dict)
        self._camera_provider.camera_params = camera_params
        self._camera_params_gui.value = camera_params

    def _show_cam_button(self) -> None:
        started = self._camera_provider.started()
        with imgui_ctx.begin_horizontal("CamButton"):
            imgui.spring()
            button_size = hello_imgui.em_to_vec2(3, 3)
            if not started:
                if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_PLAY, button_size):
                    self._camera_provider.start()
            else:
                if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_STOP, button_size):
                    self._camera_provider.stop()
            imgui.spring()

    def _internal_state_gui(self) -> bool:
        with fontawesome_6_ctx():
            with imgui_ctx.begin_vertical("CamParams"):
                imgui.text_wrapped("(Note: some cameras may not support all the settings)")
                changed = self._camera_params_gui.gui_edit()
                if changed:
                    assert isinstance(self._camera_params_gui.value, CameraParams)
                    self._camera_provider.apply_params(self._camera_params_gui.value)
                imgui.text("Start/Stop Camera")
                self._show_cam_button()

        return False
