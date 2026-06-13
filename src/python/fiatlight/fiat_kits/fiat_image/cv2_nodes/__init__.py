"""OpenCV image-processing nodes for fiatlight.

A batteries-included set of cv2 wrappers, each decorated with `fiat_tags` so it
can be dropped into a fiatlight function graph / palette. `cv2_nodes()` returns
the full set in a stable order, grouped by intent.

These wrap `cv2` (and one `cv2.xphoto` node), so they require opencv to be
installed. Tags live on each function (single source of truth); apps that want a
different taxonomy can override per function with `add_fiat_attributes`.
"""
from typing import Callable, List, Any

from fiatlight.fiat_utils.fiat_attributes_decorator import add_fiat_attributes, add_fiat_tags
from fiatlight.fiat_kits.fiat_image.image_to_from_file_gui import image_from_file, image_from_file_resized
from fiatlight.fiat_kits.fiat_image.cv_color_type import color_convert
from fiatlight.fiat_kits.fiat_image.lut_functions import lut_with_params, lut_channels_in_colorspace

from .tone import applyColorMap, clahe, convertScaleAbs, equalizeHist
from .filter import GaussianBlur, Laplacian, Scharr, Sobel, bilateralFilter, boxFilter, medianBlur
from .photo import edgePreservingFilter, fastNlMeansDenoising, fastNlMeansDenoisingColored, oil_paint, stylization
from .edges import Canny
from .morphology import dilate, erode, morphologyEx
from .threshold import adaptiveThreshold, distanceTransform, threshold
from .compositing import absdiff, addWeighted, bitwise_and, bitwise_not, bitwise_or, bitwise_xor
from .geometry import copyMakeBorder, flip, pyrDown, pyrUp, resize, rotate
from .contours import drawContours, findContours
from .features import (
    HoughCircles,
    HoughLinesP,
    approxPolyDPs,
    boundingRects,
    convexHulls,
    cornerHarris,
    cornerSubPix,
    drawCircles,
    drawEllipses,
    drawLines,
    drawPoints,
    drawRects,
    drawRotatedRects,
    goodFeaturesToTrack,
    matchTemplate,
    minEnclosingCircles,
    minMaxLoc,
)
from .transforms import (
    getAffineTransform,
    getPerspectiveTransform,
    getRotationMatrix2D,
    warpAffine,
    warpPerspective,
)
from .effects import floodFill, grabCut, pencilSketch, watershed
from .histogram import calcBackProject, calcHist1D, calcHist2D
from .blobs import connectedComponents, connectedComponentsWithStats
from .image_roi import image_roi


__all__ = [
    "cv2_nodes",
    # source
    "image_from_file",
    "image_from_file_resized",
    # color / tone
    "color_convert",
    "lut_with_params",
    "lut_channels_in_colorspace",
    "applyColorMap",
    "clahe",
    "convertScaleAbs",
    "equalizeHist",
    # filter
    "GaussianBlur",
    "Laplacian",
    "Scharr",
    "Sobel",
    "bilateralFilter",
    "boxFilter",
    "medianBlur",
    # photo
    "edgePreservingFilter",
    "fastNlMeansDenoising",
    "fastNlMeansDenoisingColored",
    "oil_paint",
    "stylization",
    # edges
    "Canny",
    # morphology
    "dilate",
    "erode",
    "morphologyEx",
    # threshold
    "adaptiveThreshold",
    "distanceTransform",
    "threshold",
    # compositing
    "absdiff",
    "addWeighted",
    "bitwise_and",
    "bitwise_not",
    "bitwise_or",
    "bitwise_xor",
    # geometry
    "copyMakeBorder",
    "flip",
    "pyrDown",
    "pyrUp",
    "resize",
    "rotate",
    "image_roi",
    # contours
    "drawContours",
    "findContours",
    # features
    "HoughCircles",
    "HoughLinesP",
    "approxPolyDPs",
    "boundingRects",
    "convexHulls",
    "cornerHarris",
    "cornerSubPix",
    "drawCircles",
    "drawEllipses",
    "drawLines",
    "drawPoints",
    "drawRects",
    "drawRotatedRects",
    "goodFeaturesToTrack",
    "matchTemplate",
    "minEnclosingCircles",
    "minMaxLoc",
    # transforms
    "getAffineTransform",
    "getPerspectiveTransform",
    "getRotationMatrix2D",
    "warpAffine",
    "warpPerspective",
    # effects / segmentation
    "floodFill",
    "grabCut",
    "pencilSketch",
    "watershed",
    # histogram
    "calcBackProject",
    "calcHist1D",
    "calcHist2D",
    # blobs
    "connectedComponents",
    "connectedComponentsWithStats",
]


def cv2_nodes() -> List[Callable[..., Any]]:
    """Return every OpenCV node wrapper, grouped by intent (stable order)."""
    return [
        # source
        image_from_file_resized,
        image_from_file,
        # color / tone
        color_convert,
        lut_with_params,
        lut_channels_in_colorspace,
        equalizeHist,
        clahe,
        applyColorMap,
        convertScaleAbs,
        # filter
        GaussianBlur,
        bilateralFilter,
        medianBlur,
        boxFilter,
        Sobel,
        Scharr,
        Laplacian,
        # photo
        fastNlMeansDenoising,
        fastNlMeansDenoisingColored,
        stylization,
        edgePreservingFilter,
        oil_paint,
        # edges
        Canny,
        # morphology
        dilate,
        erode,
        morphologyEx,
        # threshold
        threshold,
        adaptiveThreshold,
        distanceTransform,
        # compositing
        bitwise_and,
        bitwise_or,
        bitwise_xor,
        bitwise_not,
        addWeighted,
        absdiff,
        # geometry
        resize,
        pyrDown,
        pyrUp,
        flip,
        rotate,
        copyMakeBorder,
        image_roi,
        # contours
        findContours,
        drawContours,
        # features
        goodFeaturesToTrack,
        cornerHarris,
        drawPoints,
        HoughLinesP,
        drawLines,
        HoughCircles,
        drawCircles,
        # contour-derived primitives
        boundingRects,
        drawRects,
        minEnclosingCircles,
        convexHulls,
        approxPolyDPs,
        drawRotatedRects,
        drawEllipses,
        cornerSubPix,
        # template matching
        matchTemplate,
        minMaxLoc,
        # transforms
        getRotationMatrix2D,
        getAffineTransform,
        getPerspectiveTransform,
        warpAffine,
        warpPerspective,
        # effects / segmentation
        pencilSketch,
        floodFill,
        grabCut,
        watershed,
        # histogram
        calcHist1D,
        calcHist2D,
        calcBackProject,
        # blobs / connected components
        connectedComponents,
        connectedComponentsWithStats,
    ]


def _apply_kit_defaults() -> None:
    """Every node in this pack is a cv2-based image operation, so categorize the
    whole pack as `image` and add the `cv2` tag once here instead of repeating
    it on each function. (`add_fiat_tags` merges; it does not replace.)"""
    for fn in cv2_nodes():
        add_fiat_attributes(fn, fiat_category="image")
        add_fiat_tags(fn, "cv2")


_apply_kit_defaults()
