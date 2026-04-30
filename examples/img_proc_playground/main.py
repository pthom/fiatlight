"""Image-processing playground — entry point."""
import fiatlight as fl

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
    inRange,
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


ALL_WRAPPERS = [
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
    inRange,
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
    # contours
    findContours,
    drawContours,
]


def main() -> None:
    params = fl.FiatRunParams()
    # params.theme = fl.ImGuiTheme_.white_is_white
    fl.run_graph_composer(functions=ALL_WRAPPERS, params=params)


if __name__ == "__main__":
    main()
