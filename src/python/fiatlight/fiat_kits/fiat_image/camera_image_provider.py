import cv2
from pydantic import BaseModel
from fiatlight.fiat_togui.to_gui import enum_with_gui_registration, base_model_with_gui_registration
from fiatlight.fiat_types import Float_0_1, JsonDict
from fiatlight.fiat_kits.fiat_image import ImageU8_3
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from enum import Enum
from imgui_bundle import imgui, imgui_ctx  # noqa


@enum_with_gui_registration
class CameraResolution(Enum):
    HD_1280_720 = (1280, 720)
    FULL_HD_1920_1080 = (1920, 1080)
    UHD_4K_3840_2160 = (3840, 2160)
    VGA_640_480 = (640, 480)
    QVGA_320_240 = (320, 240)


@enum_with_gui_registration
class CameraFps(Enum):
    FPS_30 = 30
    FPS_60 = 60
    FPS_120 = 120
    FPS_240 = 240


@base_model_with_gui_registration
class CameraParams(BaseModel):
    device_number: int = 0
    camera_resolution: CameraResolution = CameraResolution.HD_1280_720
    fps: CameraFps = CameraFps.FPS_30
    brightness: Float_0_1 = 0.5  # type: ignore
    contrast: Float_0_1 = 0.5  # type: ignore


class CameraProvider:
    camera_params: CameraParams
    cv_cap: cv2.VideoCapture | None = None

    def __init__(self, params: CameraParams | None = None):
        if params is None:
            params = CameraParams()
        self.camera_params = params

    def get_image(self) -> ImageU8_3 | None:
        if self.cv_cap is None:
            return None
        ret, frame = self.cv_cap.read()
        if frame.shape[0] == 0 or frame.shape[1] == 0:
            return None
        return frame  # type: ignore

    def apply_params(self, params: CameraParams) -> None:
        if params == self.camera_params:
            return
        self.camera_params = params
        if self.cv_cap is None:
            return
        else:
            # self.stop()
            self._do_set_params()
            self.start()

    def start(self) -> None:
        self.cv_cap = cv2.VideoCapture()
        self.cv_cap.open(self.camera_params.device_number)
        self._do_set_params()

    def stop(self) -> None:
        if self.cv_cap is None:
            return
        self.cv_cap.release()
        self.cv_cap = None

    def started(self) -> bool:
        return self.cv_cap is not None

    def _do_set_params(self) -> None:
        assert self.cv_cap is not None
        width, height = self.camera_params.camera_resolution.value
        self.cv_cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cv_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cv_cap.set(cv2.CAP_PROP_FPS, self.camera_params.fps.value)
        self.cv_cap.set(cv2.CAP_PROP_BRIGHTNESS, self.camera_params.brightness)
        self.cv_cap.set(cv2.CAP_PROP_CONTRAST, self.camera_params.contrast)


class CameraGui(FunctionWithGui):
    _camera_provider: CameraProvider

    def __init__(self) -> None:
        super().__init__(self.f, "CameraGui")
        self._camera_provider = CameraProvider(CameraParams())
        self.internal_state_gui = self._internal_state_gui
        self.save_internal_gui_options_to_json = self._save_internal_gui_options_to_json
        self.load_internal_gui_options_from_json = self._load_internal_gui_options_from_json

        # A flag for fiatlight to set this as a live function
        self.invoke_always_dirty = True

    def f(self, params: CameraParams | None = None) -> ImageU8_3 | None:
        if params is None:
            params = CameraParams()
        self._camera_provider.apply_params(params)
        return self._camera_provider.get_image()

    def _save_internal_gui_options_to_json(self) -> JsonDict:
        r = self._camera_provider.camera_params.model_dump()
        return r

    def _load_internal_gui_options_from_json(self, json_dict: JsonDict) -> None:
        self._camera_provider.camera_params = CameraParams.validate(json_dict)
        print("ok")

    def _internal_state_gui(self) -> bool:
        from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6

        started = self._camera_provider.started()

        with fontawesome_6_ctx():
            if not started:
                if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_PLAY):
                    self._camera_provider.start()
            else:
                if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_STOP):
                    self._camera_provider.stop()

        return False
