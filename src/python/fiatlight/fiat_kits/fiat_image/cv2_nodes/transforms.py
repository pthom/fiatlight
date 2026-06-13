"""Affine and perspective transform wrappers for the playground."""
import cv2
import numpy as np

from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_kits.fiat_image import ImageU8, Matrix2x3, Matrix3x3, Points2D

from .cv_enums import BorderType, InterpolationFlag


@with_fiat_attributes(
    center_x__range=(0.0, 2000.0),
    center_y__range=(0.0, 2000.0),
    angle__range=(-180.0, 180.0),
    scale__range=(0.1, 4.0),
    fiat_tags=["transform"],
)
def getRotationMatrix2D(
    center_x: float = 100.0,
    center_y: float = 100.0,
    angle: float = 0.0,
    scale: float = 1.0,
) -> Matrix2x3:
    """Build a 2x3 affine matrix that rotates around `(center_x, center_y)` by
    `angle` degrees and uniformly scales by `scale`.

    **When to use:** Produce the transform consumed by `warpAffine` for
    arbitrary-angle rotation + uniform scaling around a chosen pivot.

    **Parameters:**
    - `center_x`, `center_y`: rotation pivot in pixel coordinates.
    - `angle`: rotation angle in degrees (counter-clockwise).
    - `scale`: uniform scale factor.

    **See also:** `warpAffine`.

    **OpenCV docs:** [cv2.getRotationMatrix2D](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html#gafbbc470ce83812914a70abfb604f4326)
    """
    m = cv2.getRotationMatrix2D((center_x, center_y), angle, scale)
    return Matrix2x3(m.astype(np.float64))


@with_fiat_attributes(
    out_width__range=(1, 4000),
    out_height__range=(1, 4000),
    fiat_tags=["transform", "geometry"],
)
def warpAffine(
    image: ImageU8,
    M: Matrix2x3,
    out_width: int = 0,
    out_height: int = 0,
    interpolation: InterpolationFlag = InterpolationFlag.INTER_LINEAR,
    borderType: BorderType = BorderType.BORDER_CONSTANT,
) -> ImageU8:
    """Apply a 2x3 affine matrix to an image.

    **When to use:** General affine warp — rotation around an arbitrary
    pivot, shear, non-uniform scale, translation. The transform `M` is
    typically produced by `getRotationMatrix2D` or `cv2.getAffineTransform`.

    **Parameters:**
    - `M`: a 2x3 affine matrix.
    - `out_width`, `out_height`: output canvas size; `0` keeps the input size.
    - `interpolation`: pixel sampling rule.
    - `borderType`: how out-of-bounds pixels are filled.

    **See also:** `getRotationMatrix2D`, `warpPerspective`, `resize`.

    **OpenCV docs:** [cv2.warpAffine](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html#ga0203d9ee5fcd28d40dbc4a1ea4451983)
    """
    h, w = image.shape[:2]
    dsize = (out_width if out_width > 0 else w, out_height if out_height > 0 else h)
    r = cv2.warpAffine(image, M, dsize, flags=interpolation.value, borderMode=borderType.value)
    return r  # type: ignore


@with_fiat_attributes(
    out_width__range=(1, 4000),
    out_height__range=(1, 4000),
    fiat_tags=["transform", "geometry"],
)
def warpPerspective(
    image: ImageU8,
    M: Matrix3x3,
    out_width: int = 0,
    out_height: int = 0,
    interpolation: InterpolationFlag = InterpolationFlag.INTER_LINEAR,
    borderType: BorderType = BorderType.BORDER_CONSTANT,
) -> ImageU8:
    """Apply a 3x3 perspective matrix to an image.

    **When to use:** Perspective rectification (e.g. straightening a
    photographed document). `M` is typically produced by
    `cv2.getPerspectiveTransform` from four source/target point pairs,
    or by `cv2.findHomography`.

    **Parameters:**
    - `M`: a 3x3 perspective matrix.
    - `out_width`, `out_height`: output canvas size; `0` keeps the input size.
    - `interpolation`: pixel sampling rule.
    - `borderType`: how out-of-bounds pixels are filled.

    **See also:** `warpAffine`.

    **OpenCV docs:** [cv2.warpPerspective](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html#gaf73673a7e8e18ec6963e3774e6a94b7c)
    """
    h, w = image.shape[:2]
    dsize = (out_width if out_width > 0 else w, out_height if out_height > 0 else h)
    r = cv2.warpPerspective(image, M, dsize, flags=interpolation.value, borderMode=borderType.value)
    return r  # type: ignore


@with_fiat_attributes(fiat_tags=["transform"])
def getAffineTransform(src: Points2D, dst: Points2D) -> Matrix2x3:
    """Solve for the 2x3 affine matrix that maps `src` → `dst`.

    **When to use:** Build the matrix for `warpAffine` from three
    source/target point pairs (rotation + scale + shear + translation).

    Both `src` and `dst` must contain **exactly 3 points**.

    **See also:** `warpAffine`, `getPerspectiveTransform`.

    **OpenCV docs:** [cv2.getAffineTransform](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html#ga8f6d378f9f8eebb5cb55cd3ae295a999)
    """
    if src.shape != (3, 2) or dst.shape != (3, 2):
        raise ValueError(f"getAffineTransform: src and dst must be (3, 2); got {src.shape} and {dst.shape}")
    m = cv2.getAffineTransform(src.astype(np.float32), dst.astype(np.float32))
    return Matrix2x3(m.astype(np.float64))


@with_fiat_attributes(fiat_tags=["transform"])
def getPerspectiveTransform(src: Points2D, dst: Points2D) -> Matrix3x3:
    """Solve for the 3x3 perspective matrix that maps `src` → `dst`.

    **When to use:** Build the matrix for `warpPerspective` from four
    source/target corner pairs (e.g. straighten a photographed document).

    Both `src` and `dst` must contain **exactly 4 points**.

    **See also:** `warpPerspective`, `getAffineTransform`.

    **OpenCV docs:** [cv2.getPerspectiveTransform](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html#ga20f62aa3235d869c9956436c67f5ec57)
    """
    if src.shape != (4, 2) or dst.shape != (4, 2):
        raise ValueError(f"getPerspectiveTransform: src and dst must be (4, 2); got {src.shape} and {dst.shape}")
    m = cv2.getPerspectiveTransform(src.astype(np.float32), dst.astype(np.float32))
    return Matrix3x3(m.astype(np.float64))
