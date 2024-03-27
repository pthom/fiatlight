from typing import List
from fiatlight.fiat_types import Function
from fiatlight.fiat_core import FunctionWithGuiFactory, to_function_with_gui_factory, gui_factories
from fiatlight.fiat_image import ImageU8, ImageU8_GRAY
from fiatlight.fiat_types import Float_0_1000
from enum import Enum

import cv2


class ApertureSize(Enum):
    Aperture_3 = 3
    Aperture_5 = 5
    Aperture_7 = 7


gui_factories().register_enum(ApertureSize)


def canny(
    image: ImageU8,
    t_lower: Float_0_1000 = 10.0,
    t_upper: Float_0_1000 = 100.0,
    aperture_size: ApertureSize = ApertureSize.Aperture_5,
    l2_gradient: bool = False,
) -> ImageU8_GRAY:
    """
    :param image: Image: Input image to which Canny filter will be applied
    :param t_lower: T_lower: Lower threshold value in Hysteresis Thresholding
    :param t_upper: Upper threshold value in Hysteresis Thresholding
    :param aperture_size: Aperture size of the Sobel filter (3, 5, 7)
    :param l2_gradient   Boolean parameter used for more precision in calculating Edge Gradient.
    :param blur_sigma: Optional sigma value for Gaussian Blur applied before Canny (skip if 0)
    :return: a binary image with edges detected using Canny filter
    """
    return cv2.Canny(image, t_lower, t_upper, apertureSize=aperture_size.value, L2gradient=l2_gradient)  # type: ignore


def blur(
    image: ImageU8,
    blur_sigma: Float_0_1000 = 0.0,
) -> ImageU8:
    """
    :param image: Image: Input image to which Gaussian Blur will be applied
    :param blur_sigma: Optional sigma value for Gaussian Blur applied to the image (skip if 0)
    :return: a blurred image
    """
    return cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)  # type: ignore


def dilate(
    image: ImageU8_GRAY,
    kernel_size: int = 3,
    iterations: int = 1,
) -> ImageU8_GRAY:
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    return cv2.dilate(image, kernel, iterations=iterations)  # type: ignore


def all_functions() -> List[FunctionWithGuiFactory]:
    bare_fn_list: List[Function] = [canny, blur, dilate]
    factories_list: List[FunctionWithGuiFactory] = []
    r = [to_function_with_gui_factory(f) for f in bare_fn_list] + factories_list
    return r
