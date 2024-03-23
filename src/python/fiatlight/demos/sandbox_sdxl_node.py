# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis

# mypy: disable-error-code="no-untyped-call"
from diffusers import AutoPipelineForText2Image
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
import torch
import numpy as np
from enum import Enum

import cv2

import fiatlight
from fiatlight import FunctionsGraph, fiat_run
from fiatlight import computer_vision
from fiatlight.computer_vision import ImageU8


class DeviceType(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class StableDiffusionXLWrapper:
    # device = "cpu"
    # device = "cuda"
    device: DeviceType = DeviceType.MPS
    pipe: StableDiffusionXLPipeline
    generator: torch.Generator

    def __init__(self) -> None:
        self._init_from_pretrained()

    def _init_from_pretrained(self) -> None:
        # Will download to ~/.cache/huggingface/transformers
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
        )
        self.pipe = self.pipe.to(self.device.value)
        self.generator = torch.Generator(device=self.device.value)
        self.generator.manual_seed(42)

        # if cpu:
        # pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", variant="fp16")
        # pipe = pipe.to("cpu")

    def query(
        self,
        prompt: str = "A cinematic shot of a baby racoon wearing an intricate italian priest robe.",
        seed: int = 42,
        num_inference_steps: int = 1,
        guidance_scale: float = 0.0,
    ) -> ImageU8:
        self.generator.manual_seed(seed)
        r = self.pipe.__call__(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=self.generator,
        )
        image = r.images[0]
        as_array = np.array(image)
        as_array = cv2.cvtColor(as_array, cv2.COLOR_RGB2BGR)
        return as_array  # type: ignore


_stable_diffusion_xl_wrapper = StableDiffusionXLWrapper()


def stable_diffusion_xl(
    prompt: str = "A cinematic shot of a baby racoon wearing an intricate italian priest robe.",
    seed: int = 42,
    num_inference_steps: int = 1,
    guidance_scale: float = 0.0,
) -> ImageU8:
    """Generates an image using the Stable Diffusion XL model."""
    return _stable_diffusion_xl_wrapper.query(prompt, seed, num_inference_steps, guidance_scale)


def oil_paint(image: ImageU8, size: int = 1, dynRatio: int = 3) -> ImageU8:
    """Applies oil painting effect to an image, using the OpenCV xphoto module."""
    return cv2.xphoto.oilPainting(image, size, dynRatio, cv2.COLOR_BGR2HSV)  # type: ignore


def main() -> None:
    stable_diffusion_xl_gui = fiatlight.any_function_to_function_with_gui(stable_diffusion_xl)
    stable_diffusion_xl_gui.invoke_automatically = False
    prompt_input = stable_diffusion_xl_gui.input_of_name("prompt")
    assert isinstance(prompt_input, fiatlight.core.StrWithGui)
    prompt_input.params.edit_type = fiatlight.core.StrEditType.multiline
    prompt_input.params.width_em = 60

    graph = FunctionsGraph.from_function_composition(
        [stable_diffusion_xl_gui, computer_vision.lut_channels_in_colorspace, oil_paint]
    )

    fiat_run(graph)


if __name__ == "__main__":
    main()
