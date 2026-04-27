"""Image-processing playground — entry point.

Phase 1: full v0 atomic-wrapper palette (no per-node tags yet, no palette UX
upgrade yet — those land in Phases 2 and 4 respectively).
"""
import fiatlight as fl

from examples.img_proc_playground.wrappers.source import image_source, imread_rgb
from examples.img_proc_playground.wrappers.color import color_convert
from examples.img_proc_playground.wrappers.lut import lut_with_params, lut_channels_in_colorspace
from examples.img_proc_playground.wrappers.filter import gaussian_blur, bilateral_filter
from examples.img_proc_playground.wrappers.edges import canny
from examples.img_proc_playground.wrappers.morphology import dilate, erode
from examples.img_proc_playground.wrappers.threshold import threshold, adaptive_threshold
from examples.img_proc_playground.wrappers.compositing import bitwise_and, bitwise_or
from examples.img_proc_playground.wrappers.geometry import resize


ALL_WRAPPERS = [
    # source
    image_source,
    imread_rgb,
    # color
    color_convert,
    lut_with_params,
    lut_channels_in_colorspace,
    # filter
    gaussian_blur,
    bilateral_filter,
    # edges
    canny,
    # morphology
    dilate,
    erode,
    # threshold
    threshold,
    adaptive_threshold,
    # compositing
    bitwise_and,
    bitwise_or,
    # geometry
    resize,
]


SANE_COMPOSITION = [
    image_source,
    # resize,
    color_convert,
    # gaussian_blur,
    # canny,
    threshold,
    # dilate,
    # erode
]

def main() -> None:
    fl.run(SANE_COMPOSITION, app_name="img_proc_playground")


if __name__ == "__main__":
    main()
