import fiatlight
from fiatlight import fiat_core
from fiatlight.fiat_image import ImageU8_3, ImageU8, ImageU8_GRAY, fiat_img_proc
from enum import Enum
import numpy as np

import cv2

image = cv2.imread(fiatlight.demo_assets_dir() + "/images/house.jpg")
image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0] * 0.5)))


def make_image() -> ImageU8_3:
    return image  # type: ignore


def canny(
    image: ImageU8,
    t_lower: float = 10.0,
    t_upper: float = 100.0,
    aperture_size: int = 5,
    l2_gradient: bool = False,
    blur_sigma: float = 0.0,
) -> ImageU8_GRAY:
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
        image = cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)  # type: ignore
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


def merge_toon_edges(
    image: ImageU8_3,
    edges_images: ImageU8_GRAY,
    blur_edges_sigma: float = 2.0,
    edges_intensity: float = 1.0,
    # edges_color: Tuple[int, int, int] = (0, 0, 0),
) -> ImageU8:
    """Add toon edges to the image.
    :param image: Image: Input image
    :param edges_images: binary image with edges detected using Canny filter
    :param blur_edges_sigma: Optional sigma value for Gaussian Blur applied to edges (skip if 0)
    :param edges_intensity: Intensity of the edges
    :param edges_color: Color of the edges
    """
    if blur_edges_sigma > 0:
        edges_images = cv2.GaussianBlur(edges_images, (0, 0), sigmaX=blur_edges_sigma, sigmaY=blur_edges_sigma)  # type: ignore

    # Create a RGBA image that will be overlayed on the original image
    # Its color will be constant (edges_color) and its alpha channel will be the edges_images
    edges_color = (0, 255, 0)
    overlay_rgba = np.zeros((*image.shape[:2], 4), dtype=np.uint8)
    overlay_rgba[:, :, :3] = edges_color
    overlay_rgba[:, :, 3] = (edges_images * edges_intensity).astype(np.uint8)

    # Overlay the RGBA image on the original image
    r = fiat_img_proc.overlay_alpha_image_precise(image, overlay_rgba)

    return r


def canny_with_gui() -> fiatlight.FunctionWithGui:
    """Convert canny to a function with GUI,
    then customize min / max values for the input parameters in the GUI of the canny node
    """
    canny_gui = fiatlight.to_function_with_gui(canny)

    # t_lower between 0 and 255
    t_lower_input = canny_gui.input_as("t_lower", fiat_core.FloatWithGui)
    t_lower_input.params.v_min = 0.0
    t_lower_input.params.v_max = 15000

    # t_upper between 0 and 255
    t_upper_input = canny_gui.input_as("t_upper", fiat_core.FloatWithGui)
    t_upper_input.params.v_min = 0.0
    t_upper_input.params.v_max = 15000

    # aperture_size between 3, 5, 7
    aperture_size_input = canny_gui.input_as("aperture_size", fiat_core.IntWithGui)
    aperture_size_input.params.edit_type = fiat_core.IntEditType.input
    aperture_size_input.params.v_min = 3
    aperture_size_input.params.v_max = 7
    aperture_size_input.params.input_step = 2

    return canny_gui


def main() -> None:
    functions_graph = fiatlight.FunctionsGraph.create_empty()
    # We need to pass the locals() and globals() to the add_function_composition method
    # so that the local MorseShape enum type can be analyzed and transformed into a GUI
    functions_graph.add_function_composition([make_image, canny_with_gui(), dilate])
    functions_graph.add_function(merge_toon_edges)
    functions_graph.add_link("dilate", "merge_toon_edges", "edges_images")
    functions_graph.add_link("make_image", "merge_toon_edges", "image")

    fiatlight.fiat_run(functions_graph)


if __name__ == "__main__":
    main()
