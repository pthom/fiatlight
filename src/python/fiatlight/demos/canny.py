import fiatlight
from fiatlight.computer_vision import ImageUInt8

import cv2

image = cv2.imread(fiatlight.demo_assets_dir() + "/images/house.jpg")
image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0] * 0.5)))


def make_image() -> ImageUInt8:
    return image  # type: ignore


def blur_image(image: ImageUInt8, sigma: float = 5.0) -> ImageUInt8:
    ksize = (0, 0)
    return cv2.GaussianBlur(image, ksize, sigmaX=sigma, sigmaY=sigma)  # type: ignore


def canny(image: ImageUInt8, t_lower: float = 10.0, t_upper: float = 100.0, aperture_size: int = 5) -> ImageUInt8:
    return cv2.Canny(image, t_lower, t_upper, apertureSize=aperture_size)  # type: ignore


def canny_with_gui() -> fiatlight.FunctionWithGui:
    """Convert canny to a function with GUI,
    then customize min / max values for the input parameters in the GUI of the canny node
    """
    canny_gui = fiatlight.any_function_to_function_with_gui(canny)

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

    return canny_gui


def main() -> None:
    functions = [make_image, blur_image, canny_with_gui()]
    functions_graph = fiatlight.FunctionsGraph.from_function_composition(functions, globals(), locals())  # type: ignore

    fiatlight.fiat_run(functions_graph, fiatlight.FiatGuiParams(show_image_inspector=True))


if __name__ == "__main__":
    main()
