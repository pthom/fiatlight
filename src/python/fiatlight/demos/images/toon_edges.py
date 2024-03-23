from fiatlight.fiat_image import ImageU8, ImageU8_GRAY, ImageU8_3
from fiatlight.fiat_image import fiat_img_proc
import fiatlight
import cv2
import numpy as np
from enum import Enum
from typing import Tuple
from fiatlight.fiat_types import Float_0_10000, Int_0_10, Float_0_10, Float_0_1, ImagePath


def canny(
    image: ImageU8,
    t_lower: Float_0_10000 = Float_0_10000(1000.0),
    t_upper: Float_0_10000 = Float_0_10000(5000.0),
    aperture_size: Int_0_10 = Int_0_10(3),
    l2_gradient: bool = True,
    blur_sigma: Float_0_10 = Float_0_10(0.0),
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
    image: ImageU8,
    kernel_size: int = 3,
    morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE,
    iterations: int = 1,
    blur_edges_sigma: float = 2.0,
) -> ImageU8:
    kernel = cv2.getStructuringElement(morph_shape.value, (kernel_size, kernel_size))
    r = cv2.dilate(image, kernel, iterations=iterations)
    if blur_edges_sigma > 0:
        r = cv2.GaussianBlur(r, (0, 0), sigmaX=blur_edges_sigma, sigmaY=blur_edges_sigma)
    return r  # type: ignore


def merge_toon_edges(
    image: ImageU8_3,
    edges_images: ImageU8_GRAY,
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

    # Create a RGBA image that will be overlayed on the original image
    # Its color will be constant (edges_color) and its alpha channel will be the edges_images
    edges_color = (0, 0, 0)
    overlay_rgba = np.zeros((*image.shape[:2], 4), dtype=np.uint8)
    overlay_rgba[:, :, :3] = edges_color
    overlay_rgba[:, :, 3] = (edges_images * edges_intensity).astype(np.uint8)

    # Overlay the RGBA image on the original image
    r = fiat_img_proc.overlay_alpha_image_precise(image, overlay_rgba)

    return r


def add_toon_edges(
    image: ImageU8_3,
    canny_t_lower: Float_0_10000 = 1000,  # type: ignore
    canny_t_upper: Float_0_10000 = 5000,  # type: ignore
    # canny_aperture_size: Int_0_10 = 5,  # type: ignore
    canny_l2_gradient: bool = True,
    canny_blur_sigma: Float_0_10 = 0.0,  # type: ignore
    dilate_kernel_size: Int_0_10 = 3,  # type: ignore
    dilate_morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE,
    dilate_iterations: Int_0_10 = 1,  # type: ignore
    blur_edges_sigma: Float_0_10 = 2.0,  # type: ignore
    edges_intensity: Float_0_1 = 1.0,  # type: ignore
) -> Tuple[ImageU8_3, ImageU8_GRAY, ImageU8, ImageU8]:
    canny_aperture_size = Int_0_10(5)
    edges = canny(image, canny_t_lower, canny_t_upper, canny_aperture_size, canny_l2_gradient, canny_blur_sigma)
    dilated_edges = dilate(edges, dilate_kernel_size, dilate_morph_shape, dilate_iterations, blur_edges_sigma)
    image_with_edges = merge_toon_edges(image, dilated_edges, edges_intensity)
    return image_with_edges, image, edges, dilated_edges


def image_source(image_file: ImagePath = fiatlight.demo_assets_dir() + "/images/house.jpg") -> ImageU8:  # type: ignore
    image = cv2.imread(image_file)
    if image.shape[0] > 1000:
        k = 1000 / image.shape[0]
        image = cv2.resize(image, (0, 0), fx=k, fy=k)
    return image  # type: ignore


def main() -> None:
    # image = fiatlight.demo_assets_dir() + "/images/house.jpg"
    # image = cv2.imread(image)

    graph = fiatlight.FunctionsGraph.from_function_composition([image_source, add_toon_edges])
    fiatlight.fiat_run(graph)


if __name__ == "__main__":
    main()
