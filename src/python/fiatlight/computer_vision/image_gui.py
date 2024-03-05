from fiatlight.any_data_with_gui import AnyDataGuiHandlers
from fiatlight.computer_vision.cv_color_type import ColorType
from fiatlight.computer_vision.image_types import Image, ImageUInt8
from imgui_bundle import immvision, imgui

from typing import Optional, Tuple
from dataclasses import dataclass
import numpy as np

_INSPECT_ID: int = 0


@dataclass
class ImagePresenterParams:
    color_type: Optional[ColorType] = None
    view_with_bgr_conversion: bool = True
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
    image_bgr: Optional[ImageUInt8] = None
    view_as_bgr: bool = True

    def __init__(self, image_presenter_params: ImagePresenterParams) -> None:
        self.image_presenter_params = image_presenter_params
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_presenter_params.image_display_width, 0)
        self.image_params.zoom_key = image_presenter_params.zoom_key

    def set_image(self, image: Image) -> None:
        self.image = image
        self.image_bgr = None
        self.image_params.refresh_image = True
        if self.image_presenter_params.color_type is not None:
            conversion_to_bgr = self.image_presenter_params.color_type.color_conversion_to_bgr()
            if conversion_to_bgr is not None:
                self.image_bgr = conversion_to_bgr.convert_image(self.image)  # type: ignore

    def gui(self) -> None:
        assert self.image is not None
        if self.image_bgr is not None:
            _, self.view_as_bgr = imgui.checkbox("View as BGR", self.view_as_bgr)

        if self.view_as_bgr and self.image_bgr is not None:
            immvision.image("output", self.image_bgr, self.image_params)
        else:
            immvision.image("output - BGR", self.image, self.image_params)
        if imgui.small_button("Inspect"):
            global _INSPECT_ID
            immvision.inspector_add_image(self.image, f"inspect {_INSPECT_ID}")
            _INSPECT_ID += 1

        self.image_params.refresh_image = False


def make_image_gui_handlers(params: ImageHandlerParams | None = None) -> AnyDataGuiHandlers[Image]:
    _params = params if params is not None else ImageHandlerParams()

    image_presenter = ImagePresenter(image_presenter_params=_params.presenter_params)

    def edit(x: Image) -> Tuple[bool, Image]:
        imgui.text("Edit Image")
        return False, x

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
