import fiatlight
from fiatlight.fiat_core import gui_factories
from fiatlight.fiat_image import ImageU8_3, ImageU8, ImageU8_GRAY, fiat_img_proc
from fiatlight.fiat_types import FloatInInterval
from enum import Enum
import numpy as np

import cv2


class CannyApertureSize(Enum):
    APERTURE_3 = 3
    APERTURE_5 = 5
    APERTURE_7 = 7


fiatlight.fiat_core.register_enum(CannyApertureSize)


def canny(
    image: ImageU8,
    t_lower: FloatInInterval = FloatInInterval(100, 20000, 1000.0),
    t_upper: FloatInInterval = FloatInInterval(100, 20000, 5000.0),
    aperture_size: CannyApertureSize = CannyApertureSize.APERTURE_5,
    l2_gradient: bool = True,
    blur_sigma: FloatInInterval = FloatInInterval(0, 10, 0.0),
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
    if blur_sigma.value > 0:
        image = cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)  # type: ignore
    r = cv2.Canny(image, t_lower.value, t_upper.value, apertureSize=aperture_size.value, L2gradient=l2_gradient)
    return r  # type: ignore


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
fiatlight.fiat_core.register_enum(MorphShape)


    # Create a RGBA image that will be overlayed on the original image
    # Its color will be constant (edges_color) and its alpha channel will be the edges_images
    edges_color = (0, 255, 0)
    overlay_rgba = np.zeros((*image.shape[:2], 4), dtype=np.uint8)
    overlay_rgba[:, :, :3] = edges_color
    overlay_rgba[:, :, 3] = (edges_images * edges_intensity).astype(np.uint8)

    # Overlay the RGBA image on the original image
    r = fiat_img_proc.overlay_alpha_image_precise(image, overlay_rgba)

    return r
def all_functions() -> list[Function]:
    return [canny, dilate]


def main() -> None:
    from fiatlight.fiat_image import image_source

    fiatlight.fiat_run_composition([image_source, canny, dilate])


if __name__ == "__main__":
    main()
