# Invoke SDXL 1.0 model for image generation
# Still a draft
from fiatlight.fiat_kits.fiat_image import ImageU8
from fiatlight.fiat_utils import with_fiat_attributes
from fiatlight.fiat_kits.fiat_ai.prompt import Prompt
import numpy as np
import sys

#
# Options
#
# SDXL cannot run on a CPU. INFERENCE_DEVICE_TYPE must be "cuda" or "mps" (Mac)
if sys.platform == "darwin":
    INFERENCE_DEVICE_TYPE = "mps"
else:
    INFERENCE_DEVICE_TYPE = "cuda"

# Set this to true  to reduce memory usage (cuda only, perf will be reduced!)
ENABLE_CPU_OFFLOAD_CUDA = False


#
# Delayed imports
# (We do not want to import these modules at startup, since these imports are slow)
#
from typing import TYPE_CHECKING  # noqa


from diffusers import DiffusionPipeline  # noqa
import torch  # noqa

pipe = DiffusionPipeline.from_pretrained(  # type: ignore
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16"
)
pipe.to("cuda")


class _SdxlWrapper:
    # pipe: "diffusers.AutoPipelineForText2Image"
    generator: "torch.Generator"

    def __init__(self) -> None:
        self._init_from_pretrained()
        self.generator = torch.Generator(device=INFERENCE_DEVICE_TYPE)
        self.generator.manual_seed(42)

    def _init_from_pretrained(self) -> None:
        self.pipe = pipe

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
            # num_inference_steps=num_inference_steps,
            # guidance_scale=guidance_scale,
            generator=self.generator,
        )
        if len(prompt) == 0:
            raise ValueError("Prompt must not be empty")
        image = r.images[0]
        as_array = np.array(image)
        return as_array  # type: ignore


_stable_diffusion_xl_wrapper: _SdxlWrapper | None = None


def validate_prompt(prompt: Prompt) -> Prompt:
    if len(prompt) < 3:
        raise ValueError("Prompt must be at least 3 characters long")  # --->
    return prompt


@with_fiat_attributes(
    seed__range=(0, 1000),
    label="Generate Image",
    prompt__validator=validate_prompt,
    invoke_async=True,
    seed__edit_type="slider_and_minus_plus",
)
def invoke_sdxl_draft(
    prompt: Prompt,
    seed: int = 0,
) -> ImageU8:
    """Generates an image using the Stable Diffusion XL model

    * **prompt:** Prompt for the image generation. You can use a prompt like "A beautiful sunset over the ocean."
    * **seed:** Seed for the random number generator. Each seed will generate a different image, for the same prompt.

    If you are looking for inspiration with your prompts, look at Lexica: https://lexica.art
    """
    global _stable_diffusion_xl_wrapper
    if _stable_diffusion_xl_wrapper is None:
        _stable_diffusion_xl_wrapper = _SdxlWrapper()
    return _stable_diffusion_xl_wrapper.query(prompt, seed)
