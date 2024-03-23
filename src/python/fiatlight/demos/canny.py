import fiatlight
from fiatlight.computer_vision import ImageU8
from enum import Enum

import cv2

image = cv2.imread(fiatlight.demo_assets_dir() + "/images/house.jpg")
image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0] * 0.5)))


def make_image() -> ImageU8:
    return image  # type: ignore


def canny(
    image: ImageU8,
    t_lower: float = 10.0,
    t_upper: float = 100.0,
    aperture_size: int = 5,
    l2_gradient: bool = False,
    blur_sigma: float = 0.0,
) -> ImageU8:
    """

    :param image: Image: Input image to which Canny filter will be applied
    :param t_lower: T_lower: Lower threshold value in Hysteresis Thresholding
    :param t_upper: Upper threshold value in Hysteresis Thresholding
    :param aperture_size: Aperture size of the Sobel filter.
    :param l2_gradient   Boolean parameter used for more precision in calculating Edge Gradient.
    :param blur_sigma: Optional sigma value for Gaussian Blur applied before Canny (skip if 0)
    :return: a binary image with edges detected using Canny filter
    """
    if blur_sigma > 0:
        image = cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)
    return cv2.Canny(image, t_lower, t_upper, apertureSize=aperture_size, L2gradient=l2_gradient)  # type: ignore


class MorphShape(Enum):
    MORPH_RECT = cv2.MORPH_RECT
    MORPH_CROSS = cv2.MORPH_CROSS
    MORPH_ELLIPSE = cv2.MORPH_ELLIPSE


def dilate(
    image: ImageU8, kernel_size: int = 3, morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE, iterations: int = 1
) -> ImageU8:
    kernel = cv2.getStructuringElement(morph_shape.value, (kernel_size, kernel_size))
    return cv2.dilate(image, kernel, iterations=iterations)  # type: ignore


# def add_toon_edges(image: ImageU8, edges_images: float = 0.0) -> ImageU8:


def canny_with_gui() -> fiatlight.FunctionWithGui:
    """Convert canny to a function with GUI,
    then customize min / max values for the input parameters in the GUI of the canny node
    """
    canny_gui = fiatlight.any_function_to_function_with_gui(canny)

    # t_lower between 0 and 255
    t_lower_input = canny_gui.input_of_name("t_lower")
    assert isinstance(t_lower_input, fiatlight.core.FloatWithGui)
    t_lower_input.params.v_min = 0.0
    t_lower_input.params.v_max = 15000

    # t_upper between 0 and 255
    t_upper_input = canny_gui.input_of_name("t_upper")
    assert isinstance(t_upper_input, fiatlight.core.FloatWithGui)
    t_upper_input.params.v_min = 0.0
    t_upper_input.params.v_max = 15000

    # aperture_size between 3, 5, 7
    aperture_size_input = canny_gui.input_of_name("aperture_size")
    assert isinstance(aperture_size_input, fiatlight.core.IntWithGui)
    aperture_size_input.params.edit_type = fiatlight.core.IntEditType.input
    aperture_size_input.params.v_min = 3
    aperture_size_input.params.v_max = 7
    aperture_size_input.params.input_step = 2

    return canny_gui


def main() -> None:
    functions = [make_image, canny_with_gui(), dilate]
    functions_graph = fiatlight.FunctionsGraph.from_function_composition(functions, globals(), locals())  # type: ignore

    fiatlight.fiat_run(functions_graph, fiatlight.FiatGuiParams(show_image_inspector=True))


if __name__ == "__main__":
    main()
