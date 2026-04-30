"""Photo-effect wrappers (cv2.photo module).

These are slow on large images, so all of them set `invoke_async=True` to
keep the UI responsive while the result is being computed.
"""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageBgr, ImageU8_GRAY

import cv2

from examples.img_proc_playground.fiat_cv_enums import EdgePreservingFlag


@fl.with_fiat_attributes(
    invoke_async=True,
    h__range=(1.0, 30.0),
    templateWindowSize__range=(3, 21),
    searchWindowSize__range=(3, 41),
    fiat_tags=["filter", "photo", "cv2.photo"],
)
def fastNlMeansDenoising(
    image: ImageU8_GRAY,
    h: float = 10.0,
    templateWindowSize: int = 7,
    searchWindowSize: int = 21,
) -> ImageU8_GRAY:
    """Non-local-means denoising for grayscale images.

    **When to use:** Remove Gaussian-style noise while preserving fine
    details. Slower but visibly higher quality than a simple `GaussianBlur`.

    **Parameters:**
    - `h`: filter strength. Larger = more denoising, more blur.
    - `templateWindowSize`: size of the patch used to compute weights.
    - `searchWindowSize`: size of the area searched for similar patches.

    **See also:** `fastNlMeansDenoisingColored`, `bilateralFilter`.

    **OpenCV docs:** [cv2.fastNlMeansDenoising](https://docs.opencv.org/4.13.0/d1/d79/group__photo__denoise.html#ga4c6b0031f56ea3f98f768881279ffe93)
    """
    r = cv2.fastNlMeansDenoising(image, None, h, templateWindowSize, searchWindowSize)
    return r  # type: ignore


@fl.with_fiat_attributes(
    invoke_async=True,
    h__range=(1.0, 30.0),
    hColor__range=(1.0, 30.0),
    templateWindowSize__range=(3, 21),
    searchWindowSize__range=(3, 41),
    fiat_tags=["filter", "photo", "cv2.photo"],
)
def fastNlMeansDenoisingColored(
    image: ImageBgr,
    h: float = 10.0,
    hColor: float = 10.0,
    templateWindowSize: int = 7,
    searchWindowSize: int = 21,
) -> ImageBgr:
    """Non-local-means denoising for BGR images.

    **When to use:** Same as `fastNlMeansDenoising` but for color photos.
    Internally converts to LAB, denoises luma + chroma separately, converts
    back — pass a BGR image to keep that conversion meaningful.

    **Parameters:**
    - `h`: filter strength on the luminance channel.
    - `hColor`: filter strength on the color channels.
    - `templateWindowSize`, `searchWindowSize`: as in the gray version.

    **OpenCV docs:** [cv2.fastNlMeansDenoisingColored](https://docs.opencv.org/4.13.0/d1/d79/group__photo__denoise.html#ga21abc1c8b0e15f78cd3eff672cb6c476)
    """
    r = cv2.fastNlMeansDenoisingColored(image, None, h, hColor, templateWindowSize, searchWindowSize)
    return r  # type: ignore


@fl.with_fiat_attributes(
    invoke_async=True,
    sigma_s__range=(1.0, 200.0),
    sigma_r__range=(0.0, 1.0),
    fiat_tags=["filter", "photo", "cv2.photo"],
)
def stylization(image: ImageBgr, sigma_s: float = 60.0, sigma_r: float = 0.45) -> ImageBgr:
    """Cartoon-like stylization built on edge-preserving smoothing.

    **When to use:** A one-shot "stylize" effect closer to a painterly look.

    **Parameters:**
    - `sigma_s`: spatial smoothing scale. Higher = larger flat regions.
    - `sigma_r`: range smoothing. Lower preserves more edges.

    **See also:** `edgePreservingFilter`, `bilateralFilter`.

    **OpenCV docs:** [cv2.stylization](https://docs.opencv.org/4.13.0/df/dac/group__photo__render.html#gacb0f7324017df153d7b5d095aed53206)
    """
    r = cv2.stylization(image, sigma_s=sigma_s, sigma_r=sigma_r)
    return r  # type: ignore


@fl.with_fiat_attributes(
    invoke_async=True,
    sigma_s__range=(1.0, 200.0),
    sigma_r__range=(0.0, 1.0),
    fiat_tags=["filter", "photo", "cv2.photo"],
)
def edgePreservingFilter(
    image: ImageBgr,
    flags: EdgePreservingFlag = EdgePreservingFlag.RECURS_FILTER,
    sigma_s: float = 60.0,
    sigma_r: float = 0.4,
) -> ImageBgr:
    """Edge-preserving smoothing — like `bilateralFilter`, faster on large images.

    **When to use:** Same goal as `bilateralFilter` (smooth flat regions,
    keep edges). Often a better starting point on big photos.

    **Parameters:**
    - `flags`: variant of the algorithm (`RECURS_FILTER` is faster,
      `NORMCONV_FILTER` is closer to a true bilateral filter).
    - `sigma_s`: spatial scale.
    - `sigma_r`: range scale.

    **See also:** `bilateralFilter`, `stylization`.

    **OpenCV docs:** [cv2.edgePreservingFilter](https://docs.opencv.org/4.13.0/df/dac/group__photo__render.html#gafaee2977597029bc8e35da6e67bd31f7)
    """
    r = cv2.edgePreservingFilter(image, flags=flags.value, sigma_s=sigma_s, sigma_r=sigma_r)
    return r  # type: ignore
