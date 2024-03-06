from __future__ import annotations
from fiatlight.function_with_gui import FunctionWithGui
from fiatlight.computer_vision import ImageUInt8
from fiatlight.computer_vision.image_with_gui import ImageWithGui
from fiatlight.computer_vision.cv_color_type import CvColorConversionCode
from fiatlight.fiatlight_gui import FiatlightGuiParams, fiatlight_run
from imgui_bundle import imgui
from typing import Any

import cv2
import numpy as np
import os


def demos_assets_folder() -> str:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(f"{this_dir}/../../../fiatlight_assets")
    return assets_dir


class GaussianBlurWithGui(FunctionWithGui):
    sigma_x: float = 3.0
    sigma_y: float = 3.0

    def __init__(self) -> None:
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()
        self.name = "Gaussian Blur"

        def f(x: Any) -> ImageUInt8:
            assert type(x) == np.ndarray
            ksize = (0, 0)
            blur: ImageUInt8 = cv2.GaussianBlur(x, ksize=ksize, sigmaX=self.sigma_x, sigmaY=self.sigma_y)  # type: ignore
            return blur

        self.f_impl = f

    def old_gui_params(self) -> bool:
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
        self.name = "Canny"

        def f(x: Any) -> ImageUInt8:
            assert type(x) == np.ndarray
            edge: ImageUInt8 = cv2.Canny(x, self.t_lower, self.t_upper, apertureSize=self.aperture_size)  # type: ignore
            return edge

        self.f_impl = f

    def old_gui_params(self) -> bool:
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
        self.name = "Oil Painting"

        def f(x: Any) -> ImageUInt8:
            assert type(x) == np.ndarray
            r = np.zeros_like(x)
            # pip install opencv-contrib-python
            r = cv2.xphoto.oilPainting(x, self.size, self.dynRatio, self.color_conversion)  # type: ignore
            return r

        self.f_impl = f

    def old_gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.dynRatio = imgui.slider_int("dynRatio", self.dynRatio, 1, 10)
        imgui.set_next_item_width(100)
        changed2, self.size = imgui.slider_int("size", self.size, 1, 10)
        return changed1 or changed2


def main() -> None:
    from fiatlight.functions_graph import FunctionsGraph
    from fiatlight.to_gui import any_function_to_function_with_gui
    from fiatlight.computer_vision.image_gui import make_image_gui_handlers
    from fiatlight.computer_vision.cv_color_type import ColorConversion
    from fiatlight.computer_vision.cv_color_type_gui import make_color_conversion_gui_handlers

    image = cv2.imread(demos_assets_folder() + "/images/house.jpg")
    image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0] * 0.5)))

    def make_image() -> ImageUInt8:
        return image  # type: ignore

    def color_convert(image: ImageUInt8, color_conversion: ColorConversion = ColorConversion()) -> ImageUInt8:
        return color_conversion.convert_image(image)

    from fiatlight.to_gui import ALL_GUI_HANDLERS_FACTORIES

    def make_graph_manually() -> FunctionsGraph:
        make_image_gui = any_function_to_function_with_gui(make_image)
        make_image_gui.set_output_gui_handler(make_image_gui_handlers())

        color_convert_gui = any_function_to_function_with_gui(color_convert)
        color_convert_gui.set_input_gui_handler("image", make_image_gui_handlers())
        color_convert_gui.set_input_gui_handler("color_conversion", make_color_conversion_gui_handlers())
        color_convert_gui.set_output_gui_handler(make_image_gui_handlers())

        functions = [make_image_gui, color_convert_gui]
        r = FunctionsGraph.from_function_composition(functions)
        return r

    def make_graph_with_register() -> FunctionsGraph:
        ALL_GUI_HANDLERS_FACTORIES["ImageUInt8"] = make_image_gui_handlers
        ALL_GUI_HANDLERS_FACTORIES["ColorConversion"] = make_color_conversion_gui_handlers
        color_convert_gui = any_function_to_function_with_gui(color_convert)
        color_convert_gui.set_output_gui_handler(make_image_gui_handlers(show_channels=True))
        # functions = [make_image, color_convert]
        functions = [make_image, color_convert_gui]
        r = FunctionsGraph.from_function_composition(functions)  # type: ignore
        return r

    functions_graph = make_graph_with_register()
    # functions_graph = make_graph_manually()
    fiatlight_run(
        functions_graph,
        FiatlightGuiParams(
            app_title="fiat_image",
            window_size=(1600, 1000),
            show_image_inspector=True,
        ),
    )


if __name__ == "__main__":
    main()
