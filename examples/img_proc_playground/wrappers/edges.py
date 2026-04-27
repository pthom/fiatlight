"""Edge-detection wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY
from fiatlight.fiat_types import PositiveFloat

import cv2

from examples.img_proc_playground.fiat_cv_enums import CannyApertureSize


@fl.with_fiat_attributes(
    blur_sigma__range=(0.0, 10.0),
    t_lower__range=(100.0, 10000.0),
    t_lower__slider_logarithmic=True,
    t_upper__range=(100.0, 10000.0),
    t_upper__slider_logarithmic=True,
)
def canny(
    image: ImageU8,
    t_lower: PositiveFloat = PositiveFloat(1000.0),
    t_upper: PositiveFloat = PositiveFloat(5000.0),
    aperture_size: CannyApertureSize = CannyApertureSize.APERTURE_5,
    l2_gradient: bool = True,
    blur_sigma: float = 0.0,
) -> ImageU8_GRAY:
    """Detect edges in an image using the Canny algorithm.

    **When to use:** The standard first-pass edge detector. Tune `t_lower` /
    `t_upper` to control how aggressive edge linking is; raise `blur_sigma` to
    reduce noise on busy images.

    **Parameters:**
    - `t_lower`: lower hysteresis threshold. Edges below this are discarded.
    - `t_upper`: upper hysteresis threshold. Pixels above this are seed edges.
    - `aperture_size`: Sobel aperture (3 / 5 / 7). Larger = thicker, smoother edges.
    - `l2_gradient`: use L2 norm (more accurate) vs. L1 (faster).
    - `blur_sigma`: Gaussian blur applied before Canny; 0 = skip.

    **See also:** `dilate` (thicken edges), `gaussian_blur`.

    **OpenCV docs:** [cv2.Canny](https://docs.opencv.org/4.13.0/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de)
    """
    if blur_sigma is not None and blur_sigma > 0:
        image = cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)  # type: ignore
    r = cv2.Canny(image, t_lower, t_upper, apertureSize=aperture_size.value, L2gradient=l2_gradient)
    return r  # type: ignore
