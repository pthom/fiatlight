"""Filter wrappers for the image-processing playground."""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY

import cv2

from examples.img_proc_playground.fiat_cv_enums import BorderType, GaussianKsize, SobelKsize


def _odd_int_validator(value: int) -> int:
    """Auto-correct to the nearest odd integer >= 1."""
    if value < 1:
        value = 1
    if value % 2 == 0:
        value += 1
    return value


def _sobel_dx_dy_validator(value: int) -> int:
    """`dx` / `dy` must be a non-negative integer (0, 1, or 2 in practice)."""
    if value < 0:
        raise ValueError("dx and dy must be >= 0")
    return value


def _bilateral_d_validator(d: int) -> int:
    """`d` must be >= 1. cv2 accepts 0 to compute from sigmaSpace, but for
    the playground we keep the value explicit; large values (>9) are slow."""
    if d < 1:
        raise ValueError("d must be >= 1")
    return d


@fl.with_fiat_attributes(
    sigmaX__range=(0.0, 25.0),
    sigmaY__range=(0.0, 25.0),
    fiat_tags=["filter", "cv2.imgproc"],
)
def GaussianBlur(
    image: ImageU8,
    ksize: GaussianKsize = GaussianKsize.K_5,
    sigmaX: float = 0.0,
    sigmaY: float = 0.0,
    borderType: BorderType = BorderType.BORDER_DEFAULT,
) -> ImageU8:
    """Blur an image using a Gaussian kernel.

    **When to use:** Reduce noise before edge detection or thresholding.
    Larger `ksize` and higher `sigma*` blur more aggressively.

    **Parameters:**
    - `ksize`: kernel size. Must be odd; common values are 3, 5, 7, 9, 11.
    - `sigmaX`: standard deviation in X. 0 = derive from `ksize`.
    - `sigmaY`: standard deviation in Y. 0 = use `sigmaX`.
    - `borderType`: how pixels outside the image are sampled.

    **See also:** `bilateralFilter` (edge-preserving), `Canny`.

    **OpenCV docs:** [cv2.GaussianBlur](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1)
    """
    k = ksize.value
    r = cv2.GaussianBlur(image, (k, k), sigmaX=sigmaX, sigmaY=sigmaY, borderType=borderType.value)
    return r  # type: ignore


@fl.with_fiat_attributes(
    invoke_async=True,
    d__range=(1, 15),
    d__validator=_bilateral_d_validator,
    sigmaColor__range=(1.0, 200.0),
    sigmaSpace__range=(1.0, 200.0),
    fiat_tags=["filter", "cv2.imgproc"],
)
def bilateralFilter(
    image: ImageU8,
    d: int = 9,
    sigmaColor: float = 75.0,
    sigmaSpace: float = 75.0,
) -> ImageU8:
    """Edge-preserving smoothing via bilateral filter.

    **When to use:** When you want to remove texture/noise but keep edges
    sharp — e.g. before edge detection on a noisy photo, or as the smoothing
    step of a cartoonize pipeline.
    Slow on large images: this wrapper is marked `invoke_async`, to preserve UI responsiveness.

    **Parameters:**
    - `d`: diameter of the pixel neighbourhood. ≥ 1; values above 9 are slow.
    - `sigmaColor`: how strongly colors must match to be averaged together.
      Higher = more colors are mixed (more cartoon-like).
    - `sigmaSpace`: how strongly distance limits the mixing. Higher = wider
      area sampled.

    **See also:** `GaussianBlur` (faster, doesn't preserve edges).

    **OpenCV docs:** [cv2.bilateralFilter](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#ga9d7064d478c95d60003cf839430737ed)
    """
    r = cv2.bilateralFilter(image, d, sigmaColor, sigmaSpace)
    return r  # type: ignore


@fl.with_fiat_attributes(
    ksize__range=(1, 31),
    ksize__validator=_odd_int_validator,
    fiat_tags=["filter", "cv2.imgproc"],
)
def medianBlur(image: ImageU8, ksize: int = 5) -> ImageU8:
    """Replace each pixel by the median of its `ksize`×`ksize` neighbourhood.

    **When to use:** Removing salt-and-pepper noise while keeping edges sharp.
    Median filtering is non-linear, so unlike `GaussianBlur` it does not
    smear sharp transitions.

    **Parameters:**
    - `ksize`: aperture size. Must be odd and >= 1; auto-corrected if even.

    **See also:** `GaussianBlur`, `bilateralFilter`.

    **OpenCV docs:** [cv2.medianBlur](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#ga564869aa33e58769b4469101aac458f9)
    """
    r = cv2.medianBlur(image, ksize)
    return r  # type: ignore


@fl.with_fiat_attributes(
    ksize__range=(1, 31),
    ksize__validator=_odd_int_validator,
    fiat_tags=["filter", "cv2.imgproc"],
)
def boxFilter(
    image: ImageU8,
    ksize: int = 5,
    normalize: bool = True,
    borderType: BorderType = BorderType.BORDER_DEFAULT,
) -> ImageU8:
    """Average each pixel over a `ksize`×`ksize` neighbourhood.

    **When to use:** Cheapest possible blur. For most image-quality use cases
    `GaussianBlur` is preferable; box filtering is useful when speed matters
    or when a perfectly flat kernel is desired.

    **Parameters:**
    - `ksize`: aperture size. Must be odd and >= 1; auto-corrected.
    - `normalize`: if False, returns the *sum* over the neighbourhood (can
      saturate quickly on bright images).
    - `borderType`: how pixels outside the image are sampled.

    **OpenCV docs:** [cv2.boxFilter](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#gad533230ebf2d42509547d514f7d3fbc3)
    """
    r = cv2.boxFilter(image, ddepth=-1, ksize=(ksize, ksize), normalize=normalize, borderType=borderType.value)
    return r  # type: ignore


@fl.with_fiat_attributes(
    dx__range=(0, 2),
    dx__validator=_sobel_dx_dy_validator,
    dy__range=(0, 2),
    dy__validator=_sobel_dx_dy_validator,
    scale__range=(0.0, 10.0),
    delta__range=(-128.0, 128.0),
    fiat_tags=["filter", "edges", "cv2.imgproc"],
)
def Sobel(
    image: ImageU8_GRAY,
    dx: int = 1,
    dy: int = 0,
    ksize: SobelKsize = SobelKsize.K_3,
    scale: float = 1.0,
    delta: float = 0.0,
) -> ImageU8_GRAY:
    """Compute an image derivative with the Sobel operator.

    **When to use:** Build a directional edge map. Set `dx=1, dy=0` for
    vertical edges, `dx=0, dy=1` for horizontal. Output is the **absolute
    value** of the (signed) derivative, scaled to U8 — sufficient for
    visualization. For numerical work, call `cv2.Sobel` directly with a
    floating-point `ddepth`.

    **Parameters:**
    - `dx`, `dy`: derivative orders. At least one must be > 0.
    - `ksize`: kernel size (1 = special 1×3 / 3×1 Scharr-like).
    - `scale`: optional gradient scale factor.
    - `delta`: bias added before conversion to U8.

    **See also:** `Scharr`, `Laplacian`, `Canny`.

    **OpenCV docs:** [cv2.Sobel](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#gacea54f142e81b6758cb6f375ce782c8d)
    """
    if dx == 0 and dy == 0:
        raise ValueError("Sobel: at least one of dx, dy must be > 0")
    g = cv2.Sobel(image, cv2.CV_64F, dx, dy, ksize=ksize.value, scale=scale, delta=delta)
    r = cv2.convertScaleAbs(g)
    return r  # type: ignore


@fl.with_fiat_attributes(
    scale__range=(0.0, 10.0),
    delta__range=(-128.0, 128.0),
    fiat_tags=["filter", "edges", "cv2.imgproc"],
)
def Scharr(
    image: ImageU8_GRAY,
    dx: int = 1,
    dy: int = 0,
    scale: float = 1.0,
    delta: float = 0.0,
) -> ImageU8_GRAY:
    """3×3 Scharr derivative — a more accurate Sobel alternative.

    **When to use:** When you need a directional gradient and the small
    Sobel-3 kernel is not accurate enough. Scharr has better rotational
    symmetry than `Sobel(ksize=3)` at the same cost.

    **Parameters:**
    - `dx`, `dy`: derivative orders. **Exactly one** must be 1, the other 0.
    - `scale`, `delta`: scaling and bias before U8 conversion.

    **See also:** `Sobel`, `Laplacian`.

    **OpenCV docs:** [cv2.Scharr](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#gaa13106761eedf14798f37aa2d60404c9)
    """
    if (dx, dy) not in ((1, 0), (0, 1)):
        raise ValueError("Scharr requires exactly one of dx, dy to be 1 (the other 0)")
    g = cv2.Scharr(image, cv2.CV_64F, dx, dy, scale=scale, delta=delta)
    r = cv2.convertScaleAbs(g)
    return r  # type: ignore


@fl.with_fiat_attributes(
    scale__range=(0.0, 10.0),
    delta__range=(-128.0, 128.0),
    fiat_tags=["filter", "edges", "cv2.imgproc"],
)
def Laplacian(
    image: ImageU8_GRAY,
    ksize: SobelKsize = SobelKsize.K_3,
    scale: float = 1.0,
    delta: float = 0.0,
) -> ImageU8_GRAY:
    """Second-derivative edge response via `cv2.Laplacian`.

    **When to use:** Highlight zero-crossings (rapid intensity changes) in
    all directions at once. Often pre-blurred (LoG = Laplacian-of-Gaussian)
    to reduce noise sensitivity.

    **Parameters:**
    - `ksize`: aperture size (1 / 3 / 5 / 7).
    - `scale`, `delta`: scaling and bias before U8 conversion.

    **See also:** `Sobel`, `GaussianBlur` (apply before for LoG), `Canny`.

    **OpenCV docs:** [cv2.Laplacian](https://docs.opencv.org/4.13.0/d4/d86/group__imgproc__filter.html#gad78703e4c8fe703d479c1860d76429e6)
    """
    g = cv2.Laplacian(image, cv2.CV_64F, ksize=ksize.value, scale=scale, delta=delta)
    r = cv2.convertScaleAbs(g)
    return r  # type: ignore
