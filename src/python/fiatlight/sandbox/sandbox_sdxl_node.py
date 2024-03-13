# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis

# mypy: disable-error-code="no-untyped-call"
from diffusers import AutoPipelineForText2Image
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
import torch
import numpy as np
from enum import Enum

import cv2
from fiatlight import FunctionsGraph, fiat_run
from fiatlight import computer_vision
from fiatlight.computer_vision import ImageUInt8


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
    ) -> ImageUInt8:
        self.generator.manual_seed(seed)
        r = self.pipe.__call__(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=self.generator,
        )
        image = r.images[0]
        as_array = np.array(image)
        return as_array


def oil_paint(image: ImageUInt8, size: int = 1, dynRatio: int = 3) -> ImageUInt8:
    """Applies oil painting effect to an image, using the OpenCV xphoto module."""
    return cv2.xphoto.oilPainting(image, size, dynRatio, cv2.COLOR_BGR2HSV)  # type: ignore


xlw = StableDiffusionXLWrapper()


def main() -> None:
    computer_vision.register_gui_factories()
    from fiatlight.computer_vision import ColorType  # noqa

    graph = FunctionsGraph.from_function_composition([xlw.query, computer_vision.lut_channels_in_colorspace, oil_paint])

    fiat_run(graph)


if __name__ == "__main__":
    main()
