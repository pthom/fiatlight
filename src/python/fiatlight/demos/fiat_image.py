from __future__ import annotations
from fiatlight.function_with_gui import FunctionWithGui
from fiatlight.computer_vision import ImageUInt8
from fiatlight.computer_vision.image_with_gui import ImageWithGui
from fiatlight.computer_vision.lut import Split_Lut_Merge_WithGui
from fiatlight.computer_vision.cv_color_type import CvColorConversionCode, ColorType
from fiatlight.fiatlight_gui import FiatlightGuiParams, fiatlight_run
from imgui_bundle import imgui
from typing import Any

import cv2
import numpy as np
import os


def demos_assets_folder() -> str:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(f"{this_dir}/../../../demos_assets")
    return assets_dir


class GaussianBlurWithGui(FunctionWithGui):
    sigma_x: float = 3.0
    sigma_y: float = 3.0

    def __init__(self) -> None:
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()

    def f(self, x: Any) -> ImageUInt8:
        assert type(x) == np.ndarray
        ksize = (0, 0)
        blur: ImageUInt8 = cv2.GaussianBlur(x, ksize=ksize, sigmaX=self.sigma_x, sigmaY=self.sigma_y)  # type: ignore
        return blur

    def name(self) -> str:
        return "GaussianBlur"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.sigma_x = imgui.slider_float("sigma_x", self.sigma_x, 0.1, 15.0)
        imgui.set_next_item_width(100)
        changed2, self.sigma_y = imgui.slider_float("sigma_y", self.sigma_y, 0.1, 15.0)
        return changed1 or changed2


class CannyWithGui(FunctionWithGui):
    t_lower = 100  # Lower Threshold
    t_upper = 200  # Upper threshold
    aperture_size = 5  # Aperture size (3, 5, or 7)

    def __init__(self) -> None:
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()

    def f(self, x: Any) -> ImageUInt8:
        assert type(x) == np.ndarray
        edge: ImageUInt8 = cv2.Canny(x, self.t_lower, self.t_upper, apertureSize=self.aperture_size)  # type: ignore
        return edge

    def name(self) -> str:
        return "Canny"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.t_lower = imgui.slider_int("t_lower", self.t_lower, 0, 255)
        imgui.set_next_item_width(100)
        changed2, self.t_upper = imgui.slider_int("t_upper", self.t_upper, 0, 255)
        imgui.set_next_item_width(100)

        imgui.text("Aperture")
        imgui.same_line()
        changed3 = False
        for aperture_value in [3, 5, 7]:
            clicked: bool
            clicked, self.aperture_size = imgui.radio_button(str(aperture_value), self.aperture_size, aperture_value)
            if clicked:
                changed3 = True
            imgui.same_line()
        imgui.new_line()
        return changed1 or changed2 or changed3


class OilPaintingWithGui(FunctionWithGui):
    dynRatio = 1  # image is divided by dynRatio before histogram processing
    size = 3  # size neighbouring size is 2-size+1
    color_conversion: CvColorConversionCode  # color space conversion code

    def __init__(self) -> None:
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()
        self.color_conversion = cv2.COLOR_BGR2HSV

    def f(self, x: Any) -> ImageUInt8:
        assert type(x) == np.ndarray
        r = np.zeros_like(x)
        # pip install opencv-contrib-python
        r = cv2.xphoto.oilPainting(x, self.size, self.dynRatio, self.color_conversion)  # type: ignore
        return r

    def name(self) -> str:
        return "Oil Painting"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.dynRatio = imgui.slider_int("dynRatio", self.dynRatio, 1, 10)
        imgui.set_next_item_width(100)
        changed2, self.size = imgui.slider_int("size", self.size, 1, 10)
        return changed1 or changed2


def main() -> None:
    image = cv2.imread(demos_assets_folder() + "/images/house.jpg")
    image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0] * 0.5)))

    split_lut_merge_gui = Split_Lut_Merge_WithGui(ColorType.BGR)

    functions = [split_lut_merge_gui.split, split_lut_merge_gui.lut, split_lut_merge_gui.merge, OilPaintingWithGui()]
    # functions = [GaussianBlurWithGui(), CannyWithGui()]

    fiatlight_run(
        FiatlightGuiParams(
            functions_graph=functions, app_title="fiat_image", initial_value=image, show_image_inspector=True
        )
    )


if __name__ == "__main__":
    main()
