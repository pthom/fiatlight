import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY
from fiatlight.fiat_types import PositiveFloat
from enum import Enum

import cv2


class CannyApertureSize(Enum):
    APERTURE_3 = 3
    APERTURE_5 = 5
    APERTURE_7 = 7


@fl.with_fiat_attributes(blur_sigma__range=(0.0, 10.0))
def canny(
    image: ImageU8,
    t_lower: PositiveFloat = PositiveFloat(1000.0),
    t_upper: PositiveFloat = PositiveFloat(5000.0),
    aperture_size: CannyApertureSize = CannyApertureSize.APERTURE_5,
    l2_gradient: bool = True,
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
    if blur_sigma is not None and blur_sigma > 0:
        image = cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)  # type: ignore
    r = cv2.Canny(image, t_lower, t_upper, apertureSize=aperture_size.value, L2gradient=l2_gradient)
    return r  # type: ignore


class MorphShape(Enum):
    MORPH_RECT = cv2.MORPH_RECT
    MORPH_CROSS = cv2.MORPH_CROSS
    MORPH_ELLIPSE = cv2.MORPH_ELLIPSE


@fl.with_fiat_attributes(kernel_size__range=(1, 10), iterations__range=(1, 10))
def dilate(
    image: ImageU8_GRAY,
    kernel_size: int = 2,
    morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE,
    iterations: int = 1,
) -> ImageU8_GRAY:
    """Dilate the image using the specified kernel shape and size

    This is often used to increase the thickness of detected objects in an image.
    Note: if kernel_size is 1, the dilation will do nothing.
    """
    kernel = cv2.getStructuringElement(morph_shape.value, (kernel_size, kernel_size))
    r = cv2.dilate(image, kernel, iterations=iterations)
    return r  # type: ignore


@fl.with_fiat_attributes(size__range=(1, 10), dynRatio__range=(1, 10))
def oil_paint(image: ImageU8, size: int = 1, dynRatio: int = 3) -> ImageU8:
    """Applies oil painting effect to an image, using the OpenCV xphoto module."""
    return cv2.xphoto.oilPainting(image, size, dynRatio, cv2.COLOR_BGR2HSV)  # type: ignore


all_functions = [canny, dilate, oil_paint]
