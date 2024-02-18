from __future__ import annotations
from typing import Any

from fiatlight.computer_vision.image_types import ImageUInt8
from fiatlight.any_data_with_gui import AnyDataWithGui
from imgui_bundle import immvision, imgui
from imgui_bundle import portable_file_dialogs as pfd
from fiatlight.computer_vision import cv_color_type


import numpy as np
from typing import Tuple, Optional
import cv2


class ImageWithGui(AnyDataWithGui):
    # value: Optional[ImageUInt8]
    image_params: immvision.ImageParams
    open_file_dialog: Optional[pfd.open_file] = None

    color_type: Optional[cv_color_type.ColorType] = None
    view_with_bgr_conversion: bool = True
    image_converted: Optional[ImageUInt8] = None

    _needs_refresh: bool = False

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
        color_conversion_to_bgr = self._color_conversion_to_bgr()
        if self.value is not None and color_conversion_to_bgr is not None:
            self.image_converted = color_conversion_to_bgr.convert_image(self.value)

    def refresh_image(self) -> None:
        self._needs_refresh = True

    def _color_conversion_to_bgr(self) -> Optional[cv_color_type.ColorConversion]:
        if self.color_type is not None:
            return self.color_type.color_conversion_to_bgr()
        return None

    def _gui_display_size(self) -> None:
        _, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)

    def _gui_image(self, image_id: str) -> None:
        can_convert_to_bgr = self._color_conversion_to_bgr() is not None
        if can_convert_to_bgr:
            _, self.view_with_bgr_conversion = imgui.checkbox("View as BGR", self.view_with_bgr_conversion)
        if can_convert_to_bgr and self.view_with_bgr_conversion:
            assert self.image_converted is not None
            immvision.image("output", self.image_converted, self.image_params)
        else:
            immvision.image("output - BGR", self.value, self.image_params)
        if imgui.small_button("Inspect"):
            immvision.inspector_add_image(self.value, image_id)

    def gui_data(self, function_name: str) -> None:
        if self.value is None:
            return
        self.first_frame = False
        self._gui_display_size()
        self.image_params.refresh_image = self.first_frame or self._needs_refresh
        self._gui_image(function_name)
        self._needs_refresh = False

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
    images_params: immvision.ImageParams

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
        self.value = v
        self.first_frame = True

    def gui_data(self, function_name: str) -> None:
        refresh_image = self.first_frame
        self.first_frame = False

        changed, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)
        if self.value is not None:
            for i, image in enumerate(self.value):
                self.image_params.refresh_image = refresh_image
                label = f"channel {i}"
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
    ratio = 1.2
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
