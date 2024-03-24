# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis

# mypy: disable-error-code="no-untyped-call"

import cv2

from fiatlight import FunctionsGraph, fiat_run
from fiatlight import fiat_image
from fiatlight.fiat_image import ImageU8
from fiatlight.demos.images.toon_edges import add_toon_edges
from fiatlight.demos.ai.stable_diffusion_xl_wrapper import stable_diffusion_xl_gui


def oil_paint(image: ImageU8, size: int = 1, dynRatio: int = 3) -> ImageU8:
    """Applies oil painting effect to an image, using the OpenCV xphoto module."""
    return cv2.xphoto.oilPainting(image, size, dynRatio, cv2.COLOR_BGR2HSV)  # type: ignore


def main() -> None:
    graph = FunctionsGraph.from_function_composition(
        [stable_diffusion_xl_gui(), fiat_image.lut_channels_in_colorspace, add_toon_edges, oil_paint]
    )

    fiat_run(graph)


if __name__ == "__main__":
    main()
