from __future__ import annotations
from typing import Any

from fiatlux.computer_vision.image_types import ImageUInt8
from fiatlux.any_data_with_gui import AnyDataWithGui
from fiatlux.computer_vision.cv_color_type import ColorType
from imgui_bundle import immvision, imgui
from imgui_bundle import portable_file_dialogs as pfd


import numpy as np
from typing import Tuple, Optional
import cv2


class ImageWithGui(AnyDataWithGui):
    # value: Optional[ImageUInt8]
    image_params: immvision.ImageParams
    open_file_dialog: Optional[pfd.open_file] = None

    def __init__(self, image: Optional[ImageUInt8] = None, zoom_key: str = "z", image_display_width: int = 200) -> None:
        self.value = image
        self.first_frame = True
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_display_width, 0)
        self.image_params.zoom_key = zoom_key

    def set(self, v: Any) -> None:
        assert v is None or type(v) == np.ndarray
        self.value = v
        self.first_frame = True

    def gui_data(self, function_name: str) -> None:
        self.image_params.refresh_image = self.first_frame
        _, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)
        if self.value is not None:
            immvision.image(function_name, self.value, self.image_params)
            self.first_frame = False
        if imgui.small_button("Inspect"):
            immvision.inspector_add_image(self.value, function_name)

    def gui_set_input(self) -> Optional[Any]:
        result = None
        if imgui.button("Select image file"):
            self.open_file_dialog = pfd.open_file(
                "Select image file", filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]
            )
        if self.open_file_dialog is not None and self.open_file_dialog.ready():
            if len(self.open_file_dialog.result()) == 1:
                image_file = self.open_file_dialog.result()[0]
                image = cv2.imread(image_file)
                if image is not None:
                    result = image
            self.open_file_dialog = None
        return result


class ImageChannelsWithGui(AnyDataWithGui):
    # value: Optional[ImageUInt8]  # We are displaying the different channels of this image
    images_params: immvision.ImageParams
    color_type: ColorType = ColorType.BGR

    def __init__(
        self,
        images: Optional[ImageUInt8] = None,  # images is a numpy of several image along the first axis
        zoom_key: str = "z",
        image_display_width: int = 200,
    ) -> None:
        self.value = images
        self.first_frame = True

        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_display_width, 0)
        self.image_params.zoom_key = zoom_key

    def set(self, v: Any) -> None:
        assert type(v) == np.ndarray
        self.value = v
        self.first_frame = True

    def gui_data(self, function_name: str) -> None:
        refresh_image = self.first_frame
        self.first_frame = False

        changed, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)
        if self.value is not None:
            for i, image in enumerate(self.value):
                channel_name = self.color_type.channel_name(i)
                self.image_params.refresh_image = refresh_image
                label = f"{channel_name}"
                immvision.image(label, image, self.image_params)
                if imgui.small_button("Inspect"):
                    immvision.inspector_add_image(image, label)


CvSize = Tuple[int, int]


def gui_edit_size(size: CvSize) -> Tuple[bool, CvSize]:
    def modify_size_by_ratio(ratio: float) -> CvSize:
        w = int(size[0] * ratio + 0.5)
        h = int(size[1] * ratio + 0.5)
        return w, h

    changed = False
    ratio = 1.05
    imgui.push_button_repeat(True)
    imgui.text("Thumbnail size")
    imgui.same_line()
    if imgui.small_button(" smaller "):
        size = modify_size_by_ratio(1.0 / ratio)
        changed = True
    imgui.same_line()
    if imgui.small_button(" bigger "):
        size = modify_size_by_ratio(ratio)
        changed = True
    imgui.pop_button_repeat()

    return changed, size
