"""Filter wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8

import cv2

from examples.img_proc_playground.fiat_cv_enums import BorderType, GaussianKsize


def _bilateral_d_validator(d: int) -> int:
    """`d` must be >= 1. cv2 accepts 0 to compute from sigma_space, but for
    the playground we keep the value explicit; large values (>9) are slow."""
    if d < 1:
        raise ValueError("d must be >= 1")
    return d


@fl.with_fiat_attributes(
    sigma_x__range=(0.0, 25.0),
    sigma_y__range=(0.0, 25.0),
    fiat_tags=["filter", "cv2.imgproc"],
)
def gaussian_blur(
    image: ImageU8,
    ksize: GaussianKsize = GaussianKsize.K_5,
    sigma_x: float = 0.0,
    sigma_y: float = 0.0,
    border_type: BorderType = BorderType.BORDER_DEFAULT,
) -> ImageU8:
    """Blur an image using a Gaussian kernel.

    **When to use:** Reduce noise before edge detection or thresholding.
    Larger `ksize` and higher `sigma_*` blur more aggressively.

    **Parameters:**
    - `ksize`: kernel size. Must be odd; common values are 3, 5, 7, 9, 11.
    - `sigma_x`: standard deviation in X. 0 = derive from `ksize`.
    - `sigma_y`: standard deviation in Y. 0 = use `sigma_x`.
    - `border_type`: how pixels outside the image are sampled.

    **See also:** `bilateral_filter` (edge-preserving), `canny`.

    **OpenCV docs:** [cv2.GaussianBlur](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1)
    """
    k = ksize.value
    r = cv2.GaussianBlur(image, (k, k), sigmaX=sigma_x, sigmaY=sigma_y, borderType=border_type.value)
    return r  # type: ignore


@fl.with_fiat_attributes(
    invoke_async=True,
    invoke_manually=True,
    d__range=(1, 15),
    d__validator=_bilateral_d_validator,
    sigma_color__range=(1.0, 200.0),
    sigma_space__range=(1.0, 200.0),
    fiat_tags=["filter", "cv2.imgproc"],
)
def bilateral_filter(
    image: ImageU8,
    d: int = 9,
    sigma_color: float = 75.0,
    sigma_space: float = 75.0,
) -> ImageU8:
    """Edge-preserving smoothing via bilateral filter.

    **When to use:** When you want to remove texture/noise but keep edges
    sharp — e.g. before edge detection on a noisy photo, or as the smoothing
    step of a cartoonize pipeline. Slow on large images: this wrapper is
    marked `invoke_async + invoke_manually`, click the run button to apply.

    **Parameters:**
    - `d`: diameter of the pixel neighbourhood. ≥ 1; values above 9 are slow.
    - `sigma_color`: how strongly colors must match to be averaged together.
      Higher = more colors are mixed (more cartoon-like).
    - `sigma_space`: how strongly distance limits the mixing. Higher = wider
      area sampled.

    **See also:** `gaussian_blur` (faster, doesn't preserve edges).

    **OpenCV docs:** [cv2.bilateralFilter](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#ga9d7064d478c95d60003cf839430737ed)
    """
    r = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    return r  # type: ignore
