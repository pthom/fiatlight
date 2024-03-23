from fiatlight.fiat_image import ImageU8

# mypy: disable-error-code="no-untyped-call"
from diffusers import AutoPipelineForText2Image  # noqa
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline  # noqa
import torch  # noqa
import numpy as np
from enum import Enum
import cv2


class InferenceDeviceType(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


_INFERENCE_DEVICE_TYPE = InferenceDeviceType.MPS


def inference_device_type() -> str:
    return _INFERENCE_DEVICE_TYPE.value


class _StableDiffusionXLWrapper:
    pipe: StableDiffusionXLPipeline
    generator: torch.Generator

    def __init__(self) -> None:
        self._init_from_pretrained()

    def _init_from_pretrained(self) -> None:
        # Will download to ~/.cache/huggingface/transformers
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
        )
        self.pipe = self.pipe.to(inference_device_type())
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


_stable_diffusion_xl_wrapper: _StableDiffusionXLWrapper | None = None


def stable_diffusion_xl(
    prompt: str,
    seed: int = 42,
    num_inference_steps: int = 1,
    guidance_scale: float = 0.0,
) -> ImageU8:
    """Generates an image using the Stable Diffusion XL model."""
    global _stable_diffusion_xl_wrapper
    if _stable_diffusion_xl_wrapper is None:
        _stable_diffusion_xl_wrapper = _StableDiffusionXLWrapper()
    return _stable_diffusion_xl_wrapper.query(prompt, seed, num_inference_steps, guidance_scale)
