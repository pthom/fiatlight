"""Feature-detection wrappers for the image-processing playground."""
import cv2
import numpy as np

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY, Points2D


@fl.with_fiat_attributes(
    maxCorners__range=(1, 1000),
    qualityLevel__range=(0.001, 0.5),
    qualityLevel__slider_logarithmic=True,
    minDistance__range=(1.0, 100.0),
    blockSize__range=(3, 21),
    fiat_tags=["features", "cv2.imgproc"],
)
def goodFeaturesToTrack(
    image: ImageU8_GRAY,
    maxCorners: int = 100,
    qualityLevel: float = 0.01,
    minDistance: float = 10.0,
    blockSize: int = 3,
    useHarrisDetector: bool = False,
    k: float = 0.04,
) -> Points2D:
    """Shi-Tomasi corner detector — find strong corners suitable for tracking.

    **When to use:** First-pass keypoint extraction on a grayscale image.
    The output points pair naturally with `drawPoints` for visualization or
    with `cv2.calcOpticalFlowPyrLK` for sparse tracking.

    **Parameters:**
    - `maxCorners`: cap on the number of returned corners (best ones kept).
    - `qualityLevel`: minimum corner quality, as a fraction of the strongest.
      Lower = more corners, including weaker ones.
    - `minDistance`: minimum spacing in pixels between returned corners.
    - `blockSize`: neighbourhood used to compute the corner score.
    - `useHarrisDetector`: switch from Shi-Tomasi to Harris.
    - `k`: Harris free parameter (only used when `useHarrisDetector=True`).

    **See also:** `cornerHarris` (raw response map), `drawPoints`.

    **OpenCV docs:** [cv2.goodFeaturesToTrack](https://docs.opencv.org/4.13.0/dd/d1a/group__imgproc__feature.html#ga1d6bb77486c8f92d79c8793ad995d541)
    """
    raw = cv2.goodFeaturesToTrack(
        image,
        maxCorners=maxCorners,
        qualityLevel=qualityLevel,
        minDistance=minDistance,
        blockSize=blockSize,
        useHarrisDetector=useHarrisDetector,
        k=k,
    )
    if raw is None:
        return Points2D(np.empty((0, 2), dtype=np.int32))
    pts = raw.reshape(-1, 2).round().astype(np.int32)
    return Points2D(pts)


@fl.with_fiat_attributes(
    blockSize__range=(2, 21),
    ksize__range=(1, 31),
    ksize__validator=lambda v: v if v % 2 == 1 else v + 1,
    k__range=(0.01, 0.2),
    fiat_tags=["features", "edges", "cv2.imgproc"],
)
def cornerHarris(
    image: ImageU8_GRAY,
    blockSize: int = 2,
    ksize: int = 3,
    k: float = 0.04,
) -> ImageU8_GRAY:
    """Harris corner-response map (per-pixel cornerness score).

    **When to use:** Visualize the raw Harris response over the whole image.
    For a thresholded list of corner locations, prefer `goodFeaturesToTrack`
    with `useHarrisDetector=True` — it returns ranked points instead of a map.

    The cv2 output is float; this wrapper normalises to U8 for display.

    **Parameters:**
    - `blockSize`: neighbourhood used to accumulate the structure tensor.
    - `ksize`: aperture for the Sobel derivatives (must be odd).
    - `k`: Harris free parameter (typical 0.04 - 0.06).

    **See also:** `goodFeaturesToTrack`.

    **OpenCV docs:** [cv2.cornerHarris](https://docs.opencv.org/4.13.0/dd/d1a/group__imgproc__feature.html#gac1fc3598018010880e370e2f709b4345)
    """
    response = cv2.cornerHarris(image, blockSize, ksize, k)
    r = cv2.normalize(response, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return r  # type: ignore


@fl.with_fiat_attributes(
    color_r__range=(0, 255),
    color_g__range=(0, 255),
    color_b__range=(0, 255),
    radius__range=(1, 20),
    thickness__range=(-1, 5),
    fiat_tags=["features", "drawing", "cv2.imgproc"],
)
def drawPoints(
    image: ImageU8,
    points: Points2D,
    color_r: int = 0,
    color_g: int = 255,
    color_b: int = 0,
    radius: int = 4,
    thickness: int = 2,
) -> ImageU8:
    """Draw a circle marker at each point of a `Points2D` value.

    **When to use:** Visualize the output of `goodFeaturesToTrack` (or any
    other `Points2D` source) over the source image.

    **Parameters:**
    - `color_r`, `color_g`, `color_b`: marker color (RGB, 0-255 each).
    - `radius`: circle radius in pixels.
    - `thickness`: stroke width; `-1` fills the marker.

    **See also:** `goodFeaturesToTrack`, `drawContours`.

    **OpenCV docs:** [cv2.circle](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#gaf10604b069374903dbd0f0488cb43670)
    """
    out = np.ascontiguousarray(image).copy()
    color = (color_r, color_g, color_b)
    for x, y in points:
        cv2.circle(out, (int(x), int(y)), radius, color, thickness)
    return out  # type: ignore
