"""OpenCV wrappers for the image-processing playground.

`all_opencv_wrappers()` returns the full palette in a stable order grouped
by intent. Each function carries a `fiat_tags: List[str]` attribute used by
the playground's function palette to filter and group nodes.
"""
from typing import Callable, List, Any

from examples.img_proc_playground.wrappers.source import image_source, imread_rgb
from examples.img_proc_playground.wrappers.color import color_convert
from examples.img_proc_playground.wrappers.lut import lut_with_params, lut_channels_in_colorspace
from examples.img_proc_playground.wrappers.tone import (
    applyColorMap,
    clahe,
    convertScaleAbs,
    equalizeHist,
)
from examples.img_proc_playground.wrappers.filter import (
    GaussianBlur,
    Laplacian,
    Scharr,
    Sobel,
    bilateralFilter,
    boxFilter,
    medianBlur,
)
from examples.img_proc_playground.wrappers.photo import (
    edgePreservingFilter,
    fastNlMeansDenoising,
    fastNlMeansDenoisingColored,
    stylization,
)
from examples.img_proc_playground.wrappers.edges import Canny
from examples.img_proc_playground.wrappers.morphology import dilate, erode, morphologyEx
from examples.img_proc_playground.wrappers.threshold import (
    adaptiveThreshold,
    distanceTransform,
    threshold,
)
from examples.img_proc_playground.wrappers.compositing import (
    absdiff,
    addWeighted,
    bitwise_and,
    bitwise_not,
    bitwise_or,
    bitwise_xor,
)
from examples.img_proc_playground.wrappers.geometry import (
    copyMakeBorder,
    flip,
    pyrDown,
    pyrUp,
    resize,
    rotate,
)
from examples.img_proc_playground.wrappers.contours import drawContours, findContours
from examples.img_proc_playground.wrappers.features import (
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
    fitEllipses,
    goodFeaturesToTrack,
    matchTemplate,
    minAreaRects,
    minEnclosingCircles,
    minMaxLoc,
)
from examples.img_proc_playground.wrappers.transforms import (
    getAffineTransform,
    getPerspectiveTransform,
    getRotationMatrix2D,
    warpAffine,
    warpPerspective,
)
from examples.img_proc_playground.wrappers.effects import (
    floodFill,
    grabCut,
    pencilSketch,
    watershed,
)
from examples.img_proc_playground.wrappers.histogram import (
    calcBackProject,
    calcHist1D,
    calcHist2D,
)
from examples.img_proc_playground.wrappers.flow import calcOpticalFlowPyrLK
from examples.img_proc_playground.wrappers.blobs import (
    connectedComponents,
    connectedComponentsWithStats,
)
from examples.img_proc_playground.wrappers.image_roi import image_roi


def all_opencv_wrappers() -> List[Callable[..., Any]]:
    """Return every OpenCV wrapper, grouped by intent."""
    return [
        # source
        image_source,
        imread_rgb,
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
        minAreaRects,
        fitEllipses,
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
        # tracking
        calcOpticalFlowPyrLK,
        # blobs / connected components
        connectedComponents,
        connectedComponentsWithStats,
    ]
