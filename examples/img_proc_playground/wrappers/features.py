"""Feature-detection wrappers for the image-processing playground."""
import cv2
import numpy as np

import fiatlight as fl
from typing import NamedTuple

from fiatlight.fiat_kits.fiat_image import (
    Circles2D,
    Contours,
    Image,
    ImageU8,
    ImageU8_GRAY,
    ImageFloat_1,
    Lines2D,
    Point2D,
    Points2D,
    Rects2D,
    RotatedRects2D,
)
from fiatlight.fiat_types import ColorRgb


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
    return response  # type: ignore


@fl.with_fiat_attributes(
    radius__range=(1, 20),
    thickness__range=(-1, 5),
    fiat_tags=["features", "drawing", "cv2.imgproc"],
)
def drawPoints(
    image: ImageU8,
    points: Points2D,
    color: ColorRgb = ColorRgb((0, 255, 0)),
    radius: int = 4,
    thickness: int = 2,
) -> ImageU8:
    """Draw a circle marker at each point of a `Points2D` value.

    **When to use:** Visualize the output of `goodFeaturesToTrack` (or any
    other `Points2D` source) over the source image.

    **Parameters:**
    - `color`: marker color (RGB).
    - `radius`: circle radius in pixels.
    - `thickness`: stroke width; `-1` fills the marker.

    **See also:** `goodFeaturesToTrack`, `drawContours`.

    **OpenCV docs:** [cv2.circle](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#gaf10604b069374903dbd0f0488cb43670)
    """
    out = np.ascontiguousarray(image).copy()
    bgr = tuple(color)
    for x, y in points:
        cv2.circle(out, (int(x), int(y)), radius, bgr, thickness)
    return out  # type: ignore


@fl.with_fiat_attributes(
    rho__range=(1.0, 10.0),
    theta__range=(0.001, 0.1),
    threshold__range=(1, 500),
    minLineLength__range=(0, 500),
    maxLineGap__range=(0, 100),
    fiat_tags=["features", "edges", "cv2.imgproc"],
)
def HoughLinesP(
    image: ImageU8_GRAY,
    rho: float = 1.0,
    theta: float = np.pi / 180.0,
    threshold: int = 80,
    minLineLength: int = 30,
    maxLineGap: int = 10,
) -> Lines2D:
    """Probabilistic Hough line-segment detector.

    **When to use:** Find straight line segments in a binary edge map.
    Pair with `Canny` or `threshold` to produce the input mask. Output
    is a `Lines2D` value pairing naturally with `drawLines`.

    **Parameters:**
    - `rho`: distance resolution of the accumulator in pixels.
    - `theta`: angular resolution in radians (default ≈ 1°).
    - `threshold`: minimum number of votes to accept a line.
    - `minLineLength`: shorter segments are rejected.
    - `maxLineGap`: maximum allowed gap between collinear segments to
      merge them.

    **See also:** `Canny`, `drawLines`.

    **OpenCV docs:** [cv2.HoughLinesP](https://docs.opencv.org/4.13.0/dd/d1a/group__imgproc__feature.html#ga8618180a5948286384e3b7ca02f6feeb)
    """
    raw = cv2.HoughLinesP(image, rho, theta, threshold, None, minLineLength, maxLineGap)
    if raw is None:
        return Lines2D(np.empty((0, 4), dtype=np.int32))
    return Lines2D(raw.reshape(-1, 4).astype(np.int32))


@fl.with_fiat_attributes(
    thickness__range=(1, 10),
    fiat_tags=["features", "drawing", "cv2.imgproc"],
)
def drawLines(
    image: ImageU8,
    lines: Lines2D,
    color: ColorRgb = ColorRgb((0, 255, 0)),
    thickness: int = 2,
) -> ImageU8:
    """Draw a line segment for each row of a `Lines2D` value.

    **When to use:** Visualize the output of `HoughLinesP` (or any
    other `Lines2D` source) over the source image.

    **OpenCV docs:** [cv2.line](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#ga7078a9fae8c7e7d13d24dac2520ae4a2)
    """
    out = np.ascontiguousarray(image).copy()
    bgr = tuple(color)
    for x1, y1, x2, y2 in lines:
        cv2.line(out, (int(x1), int(y1)), (int(x2), int(y2)), bgr, thickness)
    return out  # type: ignore


@fl.with_fiat_attributes(
    dp__range=(1.0, 4.0),
    minDist__range=(1.0, 500.0),
    param1__range=(10.0, 500.0),
    param2__range=(1.0, 200.0),
    minRadius__range=(0, 500),
    maxRadius__range=(0, 500),
    fiat_tags=["features", "cv2.imgproc"],
)
def HoughCircles(
    image: ImageU8_GRAY,
    dp: float = 1.0,
    minDist: float = 20.0,
    param1: float = 100.0,
    param2: float = 30.0,
    minRadius: int = 0,
    maxRadius: int = 0,
) -> Circles2D:
    """Hough circle detector (gradient method).

    **When to use:** Find circular shapes in a grayscale image. Unlike
    `HoughLinesP`, this works directly on the grayscale image — no
    explicit edge map needed (it computes Canny internally using
    `param1` as the high threshold).

    **Parameters:**
    - `dp`: inverse ratio of accumulator resolution to image resolution
      (1 = same size, 2 = half).
    - `minDist`: minimum center-to-center distance between detections.
    - `param1`: high threshold passed to the internal Canny.
    - `param2`: accumulator threshold for circle centers; lower = more
      false positives.
    - `minRadius`, `maxRadius`: radius bounds (0 disables).

    **See also:** `drawCircles`, `HoughLinesP`.

    **OpenCV docs:** [cv2.HoughCircles](https://docs.opencv.org/4.13.0/dd/d1a/group__imgproc__feature.html#ga47849c3be0d0406ad3ca45db65a25d2d)
    """
    raw = cv2.HoughCircles(
        image,
        cv2.HOUGH_GRADIENT,
        dp,
        minDist,
        param1=param1,
        param2=param2,
        minRadius=minRadius,
        maxRadius=maxRadius,
    )
    if raw is None:
        return Circles2D(np.empty((0, 3), dtype=np.int32))
    return Circles2D(raw.reshape(-1, 3).round().astype(np.int32))


@fl.with_fiat_attributes(
    thickness__range=(-1, 5),
    fiat_tags=["features", "drawing", "cv2.imgproc"],
)
def drawCircles(
    image: ImageU8,
    circles: Circles2D,
    color: ColorRgb = ColorRgb((0, 255, 0)),
    thickness: int = 2,
    draw_centers: bool = True,
) -> ImageU8:
    """Draw a circle for each row of a `Circles2D` value.

    **When to use:** Visualize the output of `HoughCircles`.

    **Parameters:**
    - `color`: stroke color (RGB).
    - `thickness`: stroke width; `-1` fills.
    - `draw_centers`: also draw a small marker at each circle's center.

    **See also:** `HoughCircles`, `drawPoints`.

    **OpenCV docs:** [cv2.circle](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#gaf10604b069374903dbd0f0488cb43670)
    """
    out = np.ascontiguousarray(image).copy()
    bgr = tuple(color)
    for cx, cy, r in circles:
        cv2.circle(out, (int(cx), int(cy)), int(r), bgr, thickness)
        if draw_centers:
            cv2.circle(out, (int(cx), int(cy)), 2, bgr, -1)
    return out  # type: ignore


# ---------------------------------------------------------------------------
# Per-contour primitive shapes
# ---------------------------------------------------------------------------


@fl.with_fiat_attributes(fiat_tags=["contours", "shape", "cv2.imgproc"])
def boundingRects(contours: Contours) -> Rects2D:
    """Per-contour axis-aligned bounding rectangle.

    **When to use:** Reduce a contour list to one bbox per contour for
    quick visualization or filtering by size. Output pairs with `drawRects`.

    **OpenCV docs:** [cv2.boundingRect](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#ga103fcbda2f540f3ef1c042d6a9b35ac7)
    """
    if len(contours) == 0:
        return Rects2D(np.empty((0, 4), dtype=np.int32))
    rows = [cv2.boundingRect(c) for c in contours]
    return Rects2D(np.asarray(rows, dtype=np.int32))


@fl.with_fiat_attributes(fiat_tags=["contours", "shape", "cv2.imgproc"])
def minEnclosingCircles(contours: Contours) -> Circles2D:
    """Per-contour minimum enclosing circle.

    **When to use:** Reduce a contour list to one circle per contour
    (smallest circle that fully contains the contour). Output pairs with
    `drawCircles`.

    **OpenCV docs:** [cv2.minEnclosingCircle](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#ga8ce13c24081bbc7151e9326f412190f1)
    """
    if len(contours) == 0:
        return Circles2D(np.empty((0, 3), dtype=np.int32))
    rows = []
    for c in contours:
        (cx, cy), r = cv2.minEnclosingCircle(c)
        rows.append((int(round(cx)), int(round(cy)), int(round(r))))
    return Circles2D(np.asarray(rows, dtype=np.int32))


@fl.with_fiat_attributes(fiat_tags=["contours", "shape", "cv2.imgproc"])
def convexHulls(contours: Contours) -> Contours:
    """Per-contour convex hull.

    **When to use:** Smooth-out concavities; useful before shape analysis
    where only the outer envelope matters.

    **OpenCV docs:** [cv2.convexHull](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#ga014b28e56cb8854c0de4a211cb2be656)
    """
    return Contours([cv2.convexHull(c) for c in contours])


@fl.with_fiat_attributes(
    epsilon__range=(0.1, 50.0),
    epsilon__slider_logarithmic=True,
    fiat_tags=["contours", "shape", "cv2.imgproc"],
)
def approxPolyDPs(
    contours: Contours,
    epsilon: float = 3.0,
    closed: bool = True,
) -> Contours:
    """Per-contour Douglas-Peucker polygon simplification.

    **When to use:** Reduce contour vertex count while staying within
    `epsilon` pixels of the original curve. Higher `epsilon` = coarser
    polygon (e.g. detect rectangles, triangles).

    **Parameters:**
    - `epsilon`: max distance (in pixels) between original curve and
      approximation.
    - `closed`: treat each contour as a closed polygon (typical for
      contours from `findContours`).

    **OpenCV docs:** [cv2.approxPolyDP](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#ga0012a5fdaea70b8a9970165d98722b4c)
    """
    return Contours([cv2.approxPolyDP(c, epsilon, closed) for c in contours])


@fl.with_fiat_attributes(
    thickness__range=(-1, 5),
    fiat_tags=["features", "drawing", "cv2.imgproc"],
)
def drawRects(
    image: ImageU8,
    rects: Rects2D,
    color: ColorRgb = ColorRgb((0, 255, 0)),
    thickness: int = 2,
) -> ImageU8:
    """Draw a rectangle for each row of a `Rects2D` value.

    **When to use:** Visualize the output of `boundingRects`.

    **OpenCV docs:** [cv2.rectangle](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#ga07d2f74cadcf8e305e810ce8eed13bc9)
    """
    out = np.ascontiguousarray(image).copy()
    bgr = tuple(color)
    for x, y, w, h in rects:
        cv2.rectangle(out, (int(x), int(y)), (int(x + w), int(y + h)), bgr, thickness)
    return out  # type: ignore


# ---------------------------------------------------------------------------
# Sub-pixel corner refinement
# ---------------------------------------------------------------------------


@fl.with_fiat_attributes(
    win_size__range=(3, 21),
    max_iter__range=(1, 100),
    epsilon__range=(0.001, 1.0),
    epsilon__slider_logarithmic=True,
    fiat_tags=["features", "cv2.imgproc"],
)
def cornerSubPix(
    image: ImageU8_GRAY,
    points: Points2D,
    win_size: int = 5,
    max_iter: int = 30,
    epsilon: float = 0.01,
) -> Points2D:
    """Refine integer corner locations to sub-pixel precision.

    **When to use:** Improve `goodFeaturesToTrack` output before tracking
    or geometric estimation.

    **Parameters:**
    - `win_size`: half-side of the search window (cv2 expects odd-sided
      window of side `2*win_size + 1`).
    - `max_iter`, `epsilon`: termination criteria.

    **OpenCV docs:** [cv2.cornerSubPix](https://docs.opencv.org/4.13.0/dd/d1a/group__imgproc__feature.html#ga354e0d7c86d0d9da75de9b9701a9a87e)
    """
    if len(points) == 0:
        return points
    pts32 = points.astype(np.float32).reshape(-1, 1, 2).copy()
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iter, epsilon)
    refined = cv2.cornerSubPix(image, pts32, (win_size, win_size), (-1, -1), crit)
    return Points2D(refined.reshape(-1, 2).round().astype(np.int32))


# ---------------------------------------------------------------------------
# Per-contour rotated bounding box / ellipse fit
# ---------------------------------------------------------------------------


def _to_rotated_row(
    rr: tuple[tuple[float, float], tuple[float, float], float],
) -> tuple[float, float, float, float, float]:
    (cx, cy), (w, h), angle = rr
    return (float(cx), float(cy), float(w), float(h), float(angle))


@fl.with_fiat_attributes(
    thickness__range=(1, 5),
    fiat_tags=["features", "drawing", "cv2.imgproc"],
)
def drawRotatedRects(
    image: ImageU8,
    rects: RotatedRects2D,
    color: ColorRgb = ColorRgb((0, 255, 0)),
    thickness: int = 2,
) -> ImageU8:
    """Draw each row of a `RotatedRects2D` as an oriented rectangle.

    **OpenCV docs:** [cv2.boxPoints](https://docs.opencv.org/4.13.0/d3/dc0/group__imgproc__shape.html#gaf78d467e024b4d7936cf08397d17c6f5)
    """
    out = np.ascontiguousarray(image).copy()
    bgr = tuple(color)
    for cx, cy, w, h, angle in rects:
        box = cv2.boxPoints(((float(cx), float(cy)), (float(w), float(h)), float(angle)))
        cv2.polylines(out, [box.astype(np.int32)], True, bgr, thickness)
    return out  # type: ignore


@fl.with_fiat_attributes(
    thickness__range=(-1, 5),
    fiat_tags=["features", "drawing", "cv2.imgproc"],
)
def drawEllipses(
    image: ImageU8,
    ellipses: RotatedRects2D,
    color: ColorRgb = ColorRgb((0, 255, 0)),
    thickness: int = 2,
) -> ImageU8:
    """Draw each row of a `RotatedRects2D` as an ellipse (uses cv2.ellipse).

    **OpenCV docs:** [cv2.ellipse](https://docs.opencv.org/4.13.0/d6/d6e/group__imgproc__draw.html#ga28b2267d35786f5f890ca167236cbc69)
    """
    out = np.ascontiguousarray(image).copy()
    bgr = tuple(color)
    for cx, cy, w, h, angle in ellipses:
        cv2.ellipse(
            out,
            (int(round(float(cx))), int(round(float(cy)))),
            (int(round(float(w) / 2)), int(round(float(h) / 2))),
            float(angle),
            0,
            360,
            bgr,
            thickness,
        )
    return out  # type: ignore


# ---------------------------------------------------------------------------
# Template matching
# ---------------------------------------------------------------------------


class MinMaxLocResult(NamedTuple):
    """Output of `minMaxLoc`: the global extrema of a single-channel image."""

    min_val: float
    max_val: float
    min_loc: Point2D
    max_loc: Point2D


@fl.with_fiat_attributes(fiat_tags=["features", "template", "cv2.imgproc"])
def matchTemplate(
    image: Image,
    template: Image,
) -> ImageFloat_1:
    """Slide `template` over `image` and produce a normalized score map.

    **When to use:** Locate a known small pattern in a larger image.
    The peak of the returned score map is the best match (use
    `minMaxLoc` to extract it).

    Uses `cv2.TM_CCOEFF_NORMED` (a robust default).

    **OpenCV docs:** [cv2.matchTemplate](https://docs.opencv.org/4.13.0/df/dfb/group__imgproc__object.html#ga586ebfb0a7fb604b35a23d85391329be)
    """
    score = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    return score  # type: ignore


@fl.with_fiat_attributes(fiat_tags=["features", "cv2.core"])
def minMaxLoc(image: ImageU8_GRAY) -> MinMaxLocResult:
    """Return the global min/max values and their locations in a single-channel image.

    **When to use:** Locate the brightest/darkest pixel — typically the
    peak of a score map produced by `matchTemplate`.

    **OpenCV docs:** [cv2.minMaxLoc](https://docs.opencv.org/4.13.0/d2/de8/group__core__array.html#gab473bf2eb6d14ff97e89b355dac20707)
    """
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
    return MinMaxLocResult(
        min_val=float(min_val),
        max_val=float(max_val),
        min_loc=Point2D(x=int(min_loc[0]), y=int(min_loc[1])),
        max_loc=Point2D(x=int(max_loc[0]), y=int(max_loc[1])),
    )
