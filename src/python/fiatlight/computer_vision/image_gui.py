from fiatlight.any_data_with_gui import AnyDataGuiHandlers
from fiatlight.computer_vision.image_types import Image
from imgui_bundle import immvision, imgui
from imgui_bundle import portable_file_dialogs as pfd

from typing import Optional, Tuple, Sequence
import numpy as np
import cv2

_INSPECT_ID: int = 0


def default_image_params() -> immvision.ImageParams:
    r = immvision.ImageParams()
    r.image_display_size = (200, 0)
    r.zoom_key = "z"
    return r


class ImagePresenter:
    image_params: immvision.ImageParams
    image: Image
    image_channels: Sequence[Image]
    show_channels: bool = False

    def __init__(self, image_params: immvision.ImageParams | None = None, show_channels: bool = False) -> None:
        self.image_params = default_image_params() if image_params is None else image_params
        self.show_channels = show_channels

    def set_image(self, image: Image) -> None:
        self.image = image
        self.image_params.refresh_image = True
        if len(image.shape) == 3:
            self.image_channels = cv2.split(image)  # type: ignore

    def _gui_size(self) -> None:
        ratio = 1.2
        imgui.push_button_repeat(True)
        imgui.text("Thumbnail size")
        imgui.same_line()
        if imgui.small_button(" smaller "):
            w, h = self.image_params.image_display_size
            self.image_params.image_display_size = (int(w / ratio), int(h / ratio))
        imgui.same_line()
        if imgui.small_button(" bigger "):
            w, h = self.image_params.image_display_size
            self.image_params.image_display_size = (int(w * ratio), int(h * ratio))
        imgui.pop_button_repeat()

    def _gui_channels(self) -> None:
        for i, image_channel in enumerate(self.image_channels):
            label = f"channel {i}"
            immvision.image(label, image_channel, self.image_params)
            if imgui.small_button("Inspect"):
                global _INSPECT_ID
                immvision.inspector_add_image(image_channel, f"inspect {_INSPECT_ID} _ channel {i}")
                _INSPECT_ID += 1

    def _gui_image(self) -> None:
        immvision.image("##output", self.image, self.image_params)
        if imgui.small_button("Inspect"):
            global _INSPECT_ID
            immvision.inspector_add_image(self.image, f"inspect {_INSPECT_ID}")
            _INSPECT_ID += 1

    def gui(self) -> None:
        assert self.image is not None
        _, self.show_channels = imgui.checkbox("Show channels", self.show_channels)
        self._gui_size()
        if self.show_channels and len(self.image.shape) == 3:
            self._gui_channels()
        else:
            self._gui_image()
        self.image_params.refresh_image = False


def make_image_gui_handlers(
    image_params: immvision.ImageParams | None = None, show_channels: bool = False
) -> AnyDataGuiHandlers[Image]:
    image_presenter = ImagePresenter(image_params, show_channels)
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
                    image = new_image  # type: ignore
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
