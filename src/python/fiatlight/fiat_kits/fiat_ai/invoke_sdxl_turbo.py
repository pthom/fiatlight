# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis
# To run this, you will need to install the following packages:
#   pip install -r requirements_ai.txt
from fiatlight.fiat_kits.fiat_image import ImageU8
from fiatlight.fiat_utils import LazyModule
from fiatlight.fiat_utils import with_fiat_attributes
from .prompt import Prompt
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

if TYPE_CHECKING:
    #
    import torch  # noqa
    import diffusers  # import   # noqa
    import diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl as pipeline_stable_diffusion_xl  # import StableDiffusionXLPipeline  # noqa
else:
    torch = LazyModule("torch")
    diffusers = LazyModule("diffusers")
    pipeline_stable_diffusion_xl = LazyModule("diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl")


class _SdxlTurboWrapper:
    pipe: "diffusers.AutoPipelineForText2Image"
    generator: "torch.Generator"

    def __init__(self) -> None:
        self._init_from_pretrained()

    def _init_from_pretrained(self) -> None:
        # Will download to ~/.cache/huggingface/transformers
        self.pipe = diffusers.AutoPipelineForText2Image.from_pretrained(  # type: ignore
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
        )
        self.pipe = self.pipe.to(INFERENCE_DEVICE_TYPE)  # type: ignore
        if ENABLE_CPU_OFFLOAD_CUDA and INFERENCE_DEVICE_TYPE == "cuda":
            self.pipe.enable_model_cpu_offload()  # type: ignore
        self.generator = torch.Generator(device=INFERENCE_DEVICE_TYPE)
        self.generator.manual_seed(42)

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
        if len(prompt) == 0:
            raise ValueError("Prompt must not be empty")
        image = r.images[0]
        as_array = np.array(image)
        return as_array  # type: ignore


_stable_diffusion_xl_turbo_wrapper: _SdxlTurboWrapper | None = None


def validate_prompt(prompt: Prompt) -> Prompt:
    if len(prompt) < 3:
        raise ValueError("Prompt must be at least 3 characters long")  # --->
    return prompt


@with_fiat_attributes(
    seed__range=(0, 1000),
    label="Generate Image",
    prompt__validator=validate_prompt,
    prompt__width_em=25.0,
)
def invoke_sdxl_turbo(
    prompt: Prompt,
    seed: int = 0,
) -> ImageU8:
    """Generates an image using the Stable Diffusion XL model

    * **prompt:** Prompt for the image generation. You can use a prompt like "A beautiful sunset over the ocean."
    * **seed:** Seed for the random number generator. Each seed will generate a different image, for the same prompt.

    If you are looking for inspiration with your prompts, look at Lexica: https://lexica.art
    """
    global _stable_diffusion_xl_turbo_wrapper
    if _stable_diffusion_xl_turbo_wrapper is None:
        _stable_diffusion_xl_turbo_wrapper = _SdxlTurboWrapper()
    return _stable_diffusion_xl_turbo_wrapper.query(prompt, seed)


# Options that will control how the function is invoked in fiatlight
invoke_sdxl_turbo.invoke_async = True  # type: ignore
invoke_sdxl_turbo.seed__edit_type = "slider_and_minus_plus"  # type: ignore


def main_test_sdxl() -> None:
    import fiatlight

    fiatlight.run(invoke_sdxl_turbo)


if __name__ == "__main__":
    main_test_sdxl()
