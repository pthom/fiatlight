import fiatlight
from fiatlight.fiat_types import JsonDict, ImagePath, Int_0_1000
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_kits.fiat_image.image_types import Image, ImageU8
from imgui_bundle import immvision, imgui
from imgui_bundle import portable_file_dialogs as pfd

from typing import Optional, Sequence, TypeAlias
import numpy as np
import cv2
import json


ImagePresenterParams: TypeAlias = immvision.ImageParams


def _save_image_params_to_json(image_params: ImagePresenterParams) -> JsonDict:
    json_str = immvision.image_params_to_json(image_params)
    json_dict: JsonDict = json.loads(json_str)
    return json_dict


def _load_image_params_from_json(data: JsonDict, image_params: ImagePresenterParams) -> None:
    json_str = json.dumps(data)
    immvision.fill_image_params_from_json(json_str, image_params)


_INSPECT_ID: int = 0


def default_image_params() -> ImagePresenterParams:
    r = ImagePresenterParams()
    r.image_display_size = (200, 0)
    r.zoom_key = "z"
    return r


class ImagePresenter:
    # Cached image and channels
    image: Image
    image_channels: Sequence[Image]
    # User preferences below
    image_params: ImagePresenterParams
    show_channels: bool = False
    channel_layout_vertically: bool = False

    def __init__(self, image_params: ImagePresenterParams | None = None, show_channels: bool = False) -> None:
        self.image_params = default_image_params() if image_params is None else image_params
        self.show_channels = show_channels

    def set_image(self, image: Image) -> None:
        self.image = image
        self.image_params.refresh_image = True
        if len(image.shape) == 3:
            self.image_channels = cv2.split(image)  # type: ignore

    def _gui_channels(self) -> None:
        for i, image_channel in enumerate(self.image_channels):
            label = f"channel {i}"
            imgui.begin_group()
            immvision.image(label, image_channel, self.image_params)
            if imgui.small_button("Inspect"):
                global _INSPECT_ID
                immvision.inspector_add_image(image_channel, f"inspect {_INSPECT_ID} _ channel {i}")
                _INSPECT_ID += 1
            imgui.end_group()
            if not self.channel_layout_vertically:
                imgui.same_line()
        if not self.channel_layout_vertically:
            imgui.new_line()

    def _gui_image(self) -> None:
        immvision.image("##output", self.image, self.image_params)

        # Cancel refresh_image at the end of the frame
        # We need to delay that in case there is an opened pop-up with the same widget.
        def cancel_refresh_image():
            self.image_params.refresh_image = False

        if self.image_params.refresh_image:
            fiatlight.fire_once_at_frame_end(cancel_refresh_image)

        if imgui.small_button("Inspect"):
            global _INSPECT_ID
            immvision.inspector_add_image(self.image, f"inspect {_INSPECT_ID}")
            _INSPECT_ID += 1

    def gui(self) -> None:
        assert self.image is not None
        assert len(self.image.shape) > 0
        if len(self.image.shape) == 1:
            imgui.text("Image is 1D, cannot display")
            return
        nb_channels = 1 if len(self.image.shape) == 2 else self.image.shape[2]
        if nb_channels > 1:
            _, self.show_channels = imgui.checkbox("Show channels", self.show_channels)
            if self.show_channels:
                _, self.channel_layout_vertically = imgui.checkbox("Vertical layout", self.channel_layout_vertically)
        if self.show_channels and nb_channels > 1:
            self._gui_channels()
        else:
            self._gui_image()

    def save_gui_options_to_json(self) -> JsonDict:
        image_params = _save_image_params_to_json(self.image_params)
        r = {
            "image_params": image_params,
            "show_channels": self.show_channels,
            "channel_layout_vertically": self.channel_layout_vertically,
        }
        return r

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        image_params = data["image_params"]
        _load_image_params_from_json(image_params, self.image_params)
        self.show_channels = data["show_channels"]
        self.channel_layout_vertically = data["channel_layout_vertically"]


class ImageWithGui(AnyDataWithGui[Image]):
    image_presenter: ImagePresenter
    open_file_dialog: Optional[pfd.open_file]

    def __init__(self, image_params: immvision.ImageParams | None = None, show_channels: bool = False) -> None:
        super().__init__(Image)  # type: ignore
        self.image_presenter = ImagePresenter(image_params, show_channels)
        self.open_file_dialog = None
        self.callbacks.edit = self.edit
        self.callbacks.present_custom = self.present_custom
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = lambda: np.zeros((1, 1, 3), dtype=np.uint8)  # type: ignore
        self.callbacks.present_str = self.present_str
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        self.callbacks.present_custom_popup_possible = True

    def edit(self, value: Image) -> tuple[bool, Image]:
        changed = False
        if imgui.button("Select image file"):
            # self.open_file_dialog = pfd.open_file(
            #     "Select image file", filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]
            # )
            self.open_file_dialog = pfd.open_file("Select image file")
        if self.open_file_dialog is not None and self.open_file_dialog.ready():
            if len(self.open_file_dialog.result()) == 1:
                image_file = self.open_file_dialog.result()[0]
                new_image = cv2.imread(image_file)
                if new_image is not None:
                    value = new_image  # type: ignore
                    changed = True
            self.open_file_dialog = None
        return changed, value

    def present_custom(self, _image: Image) -> None:
        # _image is not used, as the image is set with on_change
        self.image_presenter.gui()

    @staticmethod
    def present_str(image: Image) -> str:
        r = f"Image {image.shape} {image.dtype}"
        # r += f"\n{image}"
        return r

    def on_change(self, image: Image) -> None:
        self.image_presenter.set_image(image)

    def save_gui_options_to_json(self) -> JsonDict:
        return self.image_presenter.save_gui_options_to_json()

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        self.image_presenter.load_gui_options_from_json(data)


class ImageChannelsWithGui(ImageWithGui):
    """An ImageWithGui, used when we want to display the channels of an image as separate images (in the GUI)."""

    def __init__(self) -> None:
        super().__init__(show_channels=True)


def image_source(image_file: ImagePath, max_image_size: Int_0_1000 | None = None) -> ImageU8:
    """A simple function that reads an image from a file and optionally resizes it if it is too large.

    Since image_file is of type ImagePath, it will be displayed as a file picker in the GUI
    (if not linked to another function).
    """
    image = cv2.imread(image_file)

    if max_image_size is not None:
        if image.shape[0] > max_image_size or image.shape[1] > max_image_size:
            k = max_image_size / max(image.shape[0], image.shape[1])
            assert k > 0.0
            image = cv2.resize(image, None, fx=k, fy=k)
    return image  # type: ignore
