from __future__ import annotations
from typing import Any

from fiatlux_py.computer_vision import ImageUInt8
from fiatlux_py.functions_composition_graph import AnyDataWithGui, FunctionWithGui
from fiatlux_py.computer_vision.cv_color_type import *
from imgui_bundle import immvision, imgui
from imgui_bundle import imgui_node_editor

import numpy as np
from numpy.typing import NDArray
from typing import Tuple, Optional, cast
import cv2  # type: ignore


class ImageWithGui(AnyDataWithGui):
    array: Optional[ImageUInt8]
    image_params: immvision.ImageParams

    def __init__(self, image: Optional[ImageUInt8] = None, zoom_key: str = "z", image_display_width: int = 200) -> None:
        self.array = image
        self.first_frame = True
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_display_width, 0)
        self.image_params.zoom_key = zoom_key

    def get(self) -> Optional[Any]:
        return self.array

    def set(self, v: Any) -> None:
        assert type(v) == np.ndarray
        self.array = v
        self.first_frame = True

    def gui_data(self, function_name: str) -> None:
        self.image_params.refresh_image = self.first_frame
        _, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)
        if self.array is not None:
            immvision.image(function_name, self.array, self.image_params)
            self.first_frame = False
        if imgui.small_button("Inspect"):
            immvision.inspector_add_image(self.array, function_name)

    def gui_set_input(self) -> Optional[Any]:
        from imgui_bundle import im_file_dialog as ifd

        if imgui.button("Select image file"):
            ifd.FileDialog.instance().open(
                "ImageOpenDialog",
                "Choose an image",
                "Image file (*.png*.jpg*.jpeg*.bmp*.tga).png,.jpg,.jpeg,.bmp,.tga,.*",
                False,
            )

        result = None
        imgui_node_editor.suspend_editor_canvas()
        if ifd.FileDialog.instance().is_done("ImageOpenDialog"):
            if ifd.FileDialog.instance().has_result():
                ifd_result = ifd.FileDialog.instance().get_result().path()
                image = cv2.imread(ifd_result)
                if image is not None:
                    result = image
            ifd.FileDialog.instance().close()
        imgui_node_editor.resume_editor_canvas()

        return result


class ImageChannelsWithGui(AnyDataWithGui):
    array: Optional[ImageUInt8]  # We are displaying the different channels of this image
    images_params: immvision.ImageParams
    color_type: ColorType = ColorType.BGR

    def __init__(
        self,
        images: Optional[ImageUInt8] = None,  # images is a numpy of several image along the first axis
        zoom_key: str = "z",
        image_display_width: int = 200,
    ) -> None:
        self.array = images
        self.first_frame = True

        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_display_width, 0)
        self.image_params.zoom_key = zoom_key

    def set(self, v: Any) -> None:
        assert type(v) == np.ndarray
        self.array = v
        self.first_frame = True

    def get(self) -> Optional[Any]:
        return self.array

    def gui_data(self, function_name: str) -> None:
        refresh_image = self.first_frame
        self.first_frame = False

        changed, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)
        if self.array is not None:
            for i, image in enumerate(self.array):
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
