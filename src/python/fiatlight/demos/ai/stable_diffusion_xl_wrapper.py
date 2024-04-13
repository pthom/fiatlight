# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis

from fiatlight.fiat_image import ImageU8
from fiatlight.fiat_utils import LazyModule
from fiatlight import fiat_types

import numpy as np
from enum import Enum
import cv2
import sys


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # We do not want to import these modules at startup, since these imports are slow
    import torch  # noqa
    import diffusers  # import   # noqa
    import diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl as pipeline_stable_diffusion_xl  # import StableDiffusionXLPipeline  # noqa
else:
    torch = LazyModule("torch")
    diffusers = LazyModule("diffusers")
    pipeline_stable_diffusion_xl = LazyModule("diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl")


class InferenceDeviceType(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


# Set the inference device type: By default, MPS on Mac
# SDXL cannot run on a CPU! (RuntimeError: "LayerNormKernelImpl" not implemented for 'Half')
if sys.platform == "darwin":
    _INFERENCE_DEVICE_TYPE = InferenceDeviceType.MPS
else:
    _INFERENCE_DEVICE_TYPE = InferenceDeviceType.CUDA


def inference_device_type() -> str:
    return _INFERENCE_DEVICE_TYPE.value


class _StableDiffusionXLWrapper:
    pipe: "diffusers.AutoPipelineForText2Image"
    generator: "torch.Generator"

    def __init__(self) -> None:
        self._init_from_pretrained()

    def _init_from_pretrained(self) -> None:
        # Will download to ~/.cache/huggingface/transformers
        self.pipe = diffusers.AutoPipelineForText2Image.from_pretrained(  # type: ignore
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
        )
        self.pipe = self.pipe.to(inference_device_type())  # type: ignore
        self.generator = torch.Generator(device=inference_device_type())
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
        r = self.pipe.__call__(  # type: ignore
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=self.generator,
        )
        image = r.images[0]
        as_array = np.array(image)
        as_array = cv2.cvtColor(as_array, cv2.COLOR_RGB2BGR)
        return as_array  # type: ignore


_stable_diffusion_xl_wrapper: _StableDiffusionXLWrapper | None = None


def invoke_stable_diffusion_xl(
    prompt: fiat_types.Prompt,
    seed: fiat_types.Int_0_1000 = 0,  # type: ignore
    # num_inference_steps: int = 1,
    # guidance_scale: float = 0.0,
) -> ImageU8:
    """Generates an image using the Stable Diffusion XL model.

    If you are looking for inspiration with your prompts, look at Lexica: https://lexica.art

    :param prompt: Prompt for the image generation. You can use a prompt like "A beautiful sunset over the ocean."
    :param seed: Seed for the random number generator. Each seed will generate a different image, for the same prompt.
    """
    global _stable_diffusion_xl_wrapper
    if _stable_diffusion_xl_wrapper is None:
        _stable_diffusion_xl_wrapper = _StableDiffusionXLWrapper()
    return _stable_diffusion_xl_wrapper.query(prompt, seed)


invoke_stable_diffusion_xl.invoke_automatically = False  # type: ignore
invoke_stable_diffusion_xl.invoke_automatically_can_set = True  # type: ignore
invoke_stable_diffusion_xl.invoke_async = True  # type: ignore


def main_test_sdxl() -> None:
    import fiatlight

    fiatlight.fiat_run(invoke_stable_diffusion_xl)


if __name__ == "__main__":
    main_test_sdxl()
