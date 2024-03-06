from fiatlight.any_data_with_gui import AnyDataGuiHandlers
from fiatlight.computer_vision.cv_color_type import ColorType
from fiatlight.computer_vision.image_types import Image
from imgui_bundle import immvision, imgui
from imgui_bundle import portable_file_dialogs as pfd

from typing import Optional, Tuple
from dataclasses import dataclass
import numpy as np
import cv2

_INSPECT_ID: int = 0


@dataclass
class ImagePresenterParams:
    color_type: Optional[ColorType] = None
    zoom_key: str = "z"
    image_display_width: int = 200


class ImageHandlerParams:
    presenter_params: ImagePresenterParams

    def __init__(self, presenter_params: ImagePresenterParams | None = None) -> None:
        self.presenter_params = presenter_params if presenter_params is not None else ImagePresenterParams()


class ImagePresenter:
    image_params: immvision.ImageParams
    image_presenter_params: ImagePresenterParams
    image: Image

    def __init__(self, image_presenter_params: ImagePresenterParams) -> None:
        self.image_presenter_params = image_presenter_params
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_presenter_params.image_display_width, 0)
        self.image_params.zoom_key = image_presenter_params.zoom_key

    def set_image(self, image: Image) -> None:
        self.image = image
        self.image_params.refresh_image = True
        if self.image_presenter_params.color_type is not None:
            conversion_to_bgr = self.image_presenter_params.color_type.color_conversion_to_bgr()
            if conversion_to_bgr is not None:
                self.image_bgr = conversion_to_bgr.convert_image(self.image)  # type: ignore

    def gui(self) -> None:
        assert self.image is not None
        immvision.image("##output", self.image, self.image_params)
        if imgui.small_button("Inspect"):
            global _INSPECT_ID
            immvision.inspector_add_image(self.image, f"inspect {_INSPECT_ID}")
            _INSPECT_ID += 1

        self.image_params.refresh_image = False


def make_image_gui_handlers(params: ImageHandlerParams | None = None) -> AnyDataGuiHandlers[Image]:
    _params = params if params is not None else ImageHandlerParams()

    image_presenter = ImagePresenter(image_presenter_params=_params.presenter_params)
    open_file_dialog: Optional[pfd.open_file] = None

    def edit(image: Image) -> Tuple[bool, Image]:
        nonlocal open_file_dialog
        changed = False
        if imgui.button("Select image file"):
            open_file_dialog = pfd.open_file(
                "Select image file", filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]
            )
        if open_file_dialog is not None and open_file_dialog.ready():
            if len(open_file_dialog.result()) == 1:
                image_file = open_file_dialog.result()[0]
                new_image = cv2.imread(image_file)
                if new_image is not None:
                    image = new_image
                    changed = True
            open_file_dialog = None
        return changed, image

    def present(_x: Image) -> None:
        image_presenter.gui()

    def on_changed(x: Image) -> None:
        image_presenter.set_image(x)

    def default_image() -> Image:
        # Return a 1x1 black RGB image
        return np.zeros((1, 1, 3), dtype=np.uint8)

    r = AnyDataGuiHandlers[Image]()
    r.gui_present_impl = present
    r.gui_edit_impl = edit
    r.on_change = on_changed
    r.default_value_provider = default_image
    return r
