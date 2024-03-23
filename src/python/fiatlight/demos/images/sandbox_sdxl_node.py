# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis

# mypy: disable-error-code="no-untyped-call"

import cv2

import fiatlight
from fiatlight import fiat_core
from fiatlight import FunctionsGraph, fiat_run
from fiatlight import fiat_image
from fiatlight.fiat_image import ImageU8
from fiatlight.demos.images.stable_diffusion_xl_wrapper import stable_diffusion_xl
from fiatlight.demos.images.toon_edges import add_toon_edges


def oil_paint(image: ImageU8, size: int = 1, dynRatio: int = 3) -> ImageU8:
    """Applies oil painting effect to an image, using the OpenCV xphoto module."""
    return cv2.xphoto.oilPainting(image, size, dynRatio, cv2.COLOR_BGR2HSV)  # type: ignore


def stable_diffusion_xl_gui() -> fiatlight.FunctionWithGui:
    """Convert stable_diffusion_xl to a function with GUI,
    then customize min / max values for the input parameters in the GUI of the stable_diffusion_xl node
    """
    stable_diffusion_xl_gui = fiatlight.to_function_with_gui(stable_diffusion_xl)
    # Do not invoke automatically, since the image creation can be slow (about 1 second)
    stable_diffusion_xl_gui.invoke_automatically = False

    prompt_input = stable_diffusion_xl_gui.input_of_name("prompt")
    assert isinstance(prompt_input, fiat_core.StrWithGui)
    prompt_input.params.edit_type = fiat_core.StrEditType.multiline
    prompt_input.params.width_em = 60

    return stable_diffusion_xl_gui


def main() -> None:
    graph = FunctionsGraph.from_function_composition(
        [stable_diffusion_xl_gui(), fiat_image.lut_channels_in_colorspace, add_toon_edges, oil_paint]
    )

    fiat_run(graph)


if __name__ == "__main__":
    main()
