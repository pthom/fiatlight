import copy
import logging

import cv2
import os  # noqa
from pydantic import BaseModel

from fiatlight.fiat_togui.to_gui import enum_with_gui_registration, base_model_with_gui_registration
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_kits.fiat_image import ImageU8_3
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from enum import Enum
from imgui_bundle import imgui, imgui_ctx, hello_imgui
from typing import Optional


# hack, used when building documentation: we replace the camera image with a static image
# _HACK_IMAGE: ImageU8_3 = cv2.imread(os.path.dirname(__file__) + "/paris.jpg")  # type: ignore
_HACK_IMAGE = None


@enum_with_gui_registration
class CameraResolution(Enum):
    """Some typical camera resolutions"""

    HD_1280_720 = [1280, 720]
    FULL_HD_1920_1080 = [1920, 1080]
    UHD_4K_3840_2160 = [3840, 2160]
    VGA_640_480 = [640, 480]
    QVGA_320_240 = [320, 240]


@enum_with_gui_registration
class CameraFps(Enum):
    """Some typical camera frame rates"""

    FPS_30 = 30
    FPS_60 = 60
    FPS_120 = 120
    FPS_240 = 240


@base_model_with_gui_registration(device_number__range=(0, 5), brightness__range=(0, 1), contrast__range=(0, 1))
class CameraParams(BaseModel):
    """Parameters for the camera image provider"""

    device_number: int = 0
    camera_resolution: CameraResolution = CameraResolution.VGA_640_480
    brightness: float = 0.5
    contrast: float = 0.5


class CameraImageProvider:
    """A class to provide images from a camera"""

    camera_params: CameraParams
    previous_camera_params: Optional[CameraParams] = None
    cv_cap: cv2.VideoCapture | None = None

    def __init__(self, params: Optional[CameraParams] = None):
        if params is None:
            params = CameraParams()
        self.camera_params = params

    def get_image(self) -> ImageU8_3 | None:
        if _HACK_IMAGE is not None:
            return _HACK_IMAGE
        if self.cv_cap is None:
            return None
        ret, frame = self.cv_cap.read()
        if frame is None:
            return None
        if frame.shape[0] == 0 or frame.shape[1] == 0:
            return None
        return frame  # type: ignore

    def apply_params(self, params: CameraParams) -> None:
        if self.previous_camera_params is not None and params == self.previous_camera_params:
            return
        if self.cv_cap is None:
            self.camera_params = params
            return

        shall_restart = False
        if self.previous_camera_params is not None:
            if self.previous_camera_params.device_number != params.device_number:
                shall_restart = True
            if self.previous_camera_params.camera_resolution != params.camera_resolution:
                shall_restart = True

        self.previous_camera_params = copy.deepcopy(self.camera_params)
        self.camera_params = params

        if shall_restart:
            self.stop()
            self.start()
        else:
            brightness_set = self.cv_cap.set(cv2.CAP_PROP_BRIGHTNESS, self.camera_params.brightness)
            contrast_set = self.cv_cap.set(cv2.CAP_PROP_CONTRAST, self.camera_params.contrast)
            if not brightness_set:
                logging.warning("This camera does not support setting brightness")
            if not contrast_set:
                logging.warning("This camera does not support setting contrast")

    def start(self) -> None:
        logging.info(f"CameraImageProvider start: {self.camera_params}")
        self.cv_cap = cv2.VideoCapture()
        self.cv_cap.open(self.camera_params.device_number)
        frame_width_set = self.cv_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_params.camera_resolution.value[0])
        frame_height_set = self.cv_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_params.camera_resolution.value[1])
        # fps_set = self.cv_cap.set(cv2.CAP_PROP_FPS, self.camera_params.fps.value)
        brightness_set = self.cv_cap.set(cv2.CAP_PROP_BRIGHTNESS, self.camera_params.brightness)
        contrast_set = self.cv_cap.set(cv2.CAP_PROP_CONTRAST, self.camera_params.contrast)

        if not frame_width_set or not frame_height_set:
            logging.warning("This camera does not support setting frame width and height")
        if not brightness_set:
            logging.warning("This camera does not support setting brightness")
        if not contrast_set:
            logging.warning("This camera does not support setting contrast")

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
        self._camera_params_gui = to_data_with_gui(self._camera_provider.camera_params, {})

        self.internal_state_gui = self._internal_state_gui
        self.save_internal_gui_options_to_json = self._save_internal_gui_options_to_json
        self.load_internal_gui_options_from_json = self._load_internal_gui_options_from_json

        # A flag for fiatlight to set this as a live function
        self.invoke_always_dirty = True

    def f(self) -> ImageU8_3 | None:
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
                imgui.text("Camera Parameters")
                imgui.text_wrapped("(Note: some cameras may not support all the settings)")
                changed = self._camera_params_gui.gui_edit()
                if changed:
                    assert isinstance(self._camera_params_gui.value, CameraParams)
                    self._camera_provider.apply_params(self._camera_params_gui.value)
                imgui.text("Start/Stop Camera")
                self._show_cam_button()

        return False
