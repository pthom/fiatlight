from __future__ import annotations

import cv2
import fiatlight
import os


def demos_assets_folder() -> str:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(f"{this_dir}/../../../fiatlight_assets")
    return assets_dir


def main() -> None:
    from fiatlight import FunctionsGraph, FiatGuiParams, fiat_run, any_function_to_function_with_gui
    from fiatlight.computer_vision import (
        ImageUInt8,
        ImageUInt8Channels,
        ImageWithGui,
        ColorConversionWithGui,
        lut_channels_in_colorspace,
    )

    image = cv2.imread(demos_assets_folder() + "/images/house.jpg")
    image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0] * 0.5)))

    def make_image() -> ImageUInt8:
        return image  # type: ignore

    def color_convert(
        image: ImageUInt8, color_conversion: fiatlight.computer_vision.ColorConversion | None = None
    ) -> ImageUInt8Channels:
        if color_conversion is None:
            return image
        return color_conversion.convert_image(image)

    def oil_paint(image: ImageUInt8, size: int = 1, dynRatio: int = 3) -> ImageUInt8:
        return cv2.xphoto.oilPainting(image, size, dynRatio, cv2.COLOR_BGR2HSV)  # type: ignore

    def blur_image(image: ImageUInt8, sigma: float = 5.0) -> ImageUInt8:
        ksize = (0, 0)
        return cv2.GaussianBlur(image, ksize, sigmaX=sigma, sigmaY=sigma)  # type: ignore

    def canny(image: ImageUInt8, t_lower: float = 10.0, t_upper: float = 100.0, aperture_size: int = 5) -> ImageUInt8:
        return cv2.Canny(image, t_lower, t_upper, apertureSize=aperture_size)  # type: ignore

    def make_graph_manually() -> FunctionsGraph:
        make_image_gui = fiatlight.any_function_to_function_with_gui(make_image)
        make_image_gui.set_output_gui(ImageWithGui())

        color_convert_gui = fiatlight.any_function_to_function_with_gui(color_convert)
        color_convert_gui.set_input_gui("image", ImageWithGui())
        color_convert_gui.set_input_gui("color_conversion", ColorConversionWithGui())
        color_convert_gui.set_output_gui(ImageWithGui(show_channels=True))

        functions = [make_image_gui, color_convert_gui]
        r = fiatlight.FunctionsGraph.from_function_composition(functions)
        return r

    def make_graph_with_register() -> fiatlight.FunctionsGraph:
        # Register the GUI factories
        fiatlight.computer_vision.register_gui_factories()
        # Note: computer_vision.register_gui_factories() will do this:
        #     ALL_GUI_FACTORIES["ImageUInt8"] = ImageWithGui
        #     ALL_GUI_FACTORIES["ImageUInt8Channels"] = ImageChannelsWithGui
        #     ALL_GUI_FACTORIES["ColorConversion"] = ColorConversionWithGui
        #     ALL_GUI_FACTORIES["lut.LutParams"] = LutParamsWithGui

        # functions = [make_image, color_convert]

        # (import required to get an automatic Gui for the enums in lut_channels_in_colorspace params)
        from fiatlight.computer_vision import ColorType  # noqa

        functions = [make_image, lut_channels_in_colorspace, blur_image, oil_paint]
        r = FunctionsGraph.from_function_composition(functions, globals(), locals())  # type: ignore
        return r

    def make_canny_graph() -> FunctionsGraph:
        fiatlight.computer_vision.register_gui_factories()

        # Customize min / max values for the input parameters in the GUI of the canny node
        canny_gui = any_function_to_function_with_gui(canny)

        # t_lower between 0 and 255
        t_lower_input = canny_gui.input_of_name("t_lower")
        assert isinstance(t_lower_input, fiatlight.core.FloatWithGui)
        t_lower_input.params.v_min = 0.0
        t_lower_input.params.v_max = 255.0

        # t_upper between 0 and 255
        t_upper_input = canny_gui.input_of_name("t_upper")
        assert isinstance(t_upper_input, fiatlight.core.FloatWithGui)
        t_upper_input.params.v_min = 0.0
        t_upper_input.params.v_max = 255.0

        # aperture_size between 3, 5, 7
        aperture_size_input = canny_gui.input_of_name("aperture_size")
        assert isinstance(aperture_size_input, fiatlight.core.IntWithGui)
        aperture_size_input.params.edit_type = fiatlight.core.IntEditType.input
        aperture_size_input.params.v_min = 3
        aperture_size_input.params.v_max = 7
        aperture_size_input.params.input_step = 2

        functions = [make_image, blur_image, canny_gui]
        r = FunctionsGraph.from_function_composition(functions, globals(), locals())  # type: ignore
        return r

    # functions_graph = make_graph_with_register()
    # functions_graph = make_graph_manually()
    functions_graph = make_canny_graph()

    fiat_run(
        functions_graph,
        FiatGuiParams(
            app_title="fiat_image",
            window_size=(1600, 1000),
            show_image_inspector=True,
        ),
    )


if __name__ == "__main__":
    main()
