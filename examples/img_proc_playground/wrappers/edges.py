"""Edge-detection wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY
from fiatlight.fiat_types import PositiveFloat

import cv2

from examples.img_proc_playground.fiat_cv_enums import CannyApertureSize


@fl.with_fiat_attributes(
    blur_sigma__range=(0.0, 10.0),
    threshold1__range=(100.0, 10000.0),
    threshold1__slider_logarithmic=True,
    threshold2__range=(100.0, 10000.0),
    threshold2__slider_logarithmic=True,
    fiat_tags=["edges", "cv2.imgproc"],
)
def Canny(
    image: ImageU8,
    threshold1: PositiveFloat = PositiveFloat(1000.0),
    threshold2: PositiveFloat = PositiveFloat(5000.0),
    apertureSize: CannyApertureSize = CannyApertureSize.APERTURE_5,
    L2gradient: bool = True,
    blur_sigma: float = 0.0,
) -> ImageU8_GRAY:
    """Detect edges in an image using the Canny algorithm.

    **When to use:** The standard first-pass edge detector. Tune `threshold1` /
    `threshold2` to control how aggressive edge linking is; raise `blur_sigma`
    to reduce noise on busy images.

    **Parameters:**
    - `threshold1`: lower hysteresis threshold. Edges below this are discarded.
    - `threshold2`: upper hysteresis threshold. Pixels above this are seed edges.
    - `apertureSize`: Sobel aperture (3 / 5 / 7). Larger = thicker, smoother edges.
    - `L2gradient`: use L2 norm (more accurate) vs. L1 (faster).
    - `blur_sigma`: Gaussian blur applied before Canny; 0 = skip.

    **See also:** `dilate` (thicken edges), `GaussianBlur`.

    **OpenCV docs:** [cv2.Canny](https://docs.opencv.org/4.13.0/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de)
    """
    if blur_sigma is not None and blur_sigma > 0:
        image = cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)  # type: ignore
    r = cv2.Canny(image, threshold1, threshold2, apertureSize=apertureSize.value, L2gradient=L2gradient)
    return r  # type: ignore
