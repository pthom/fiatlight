# https://huggingface.co/stabilityai/sdxl-turbo
# SDXL-Turbo is a distilled version of SDXL 1.0, trained for real-time synthesis
# To run this, you will need to install the following packages:
#   pip install -r requirements_ai.txt
from fiatlight.fiat_image import ImageU8
from fiatlight.fiat_utils import LazyModule
from fiatlight import fiat_types
import numpy as np
import cv2


#
# Options
#
# SDXL cannot run on a CPU!
INFERENCE_DEVICE_TYPE = "cuda"  # "cpu" or "cuda" or "mps" (Mac only)
# reduce memory usage
ENABLE_CPU_OFFLOAD = True


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
        self.pipe = self.pipe.to(INFERENCE_DEVICE_TYPE)  # type: ignore
        if ENABLE_CPU_OFFLOAD:
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


# Options that will control how the function is invoked in fiatlight
invoke_stable_diffusion_xl.invoke_automatically = False  # type: ignore
invoke_stable_diffusion_xl.invoke_automatically_can_set = True  # type: ignore
invoke_stable_diffusion_xl.invoke_async = True  # type: ignore


def main_test_sdxl() -> None:
    import fiatlight

    fiatlight.fiat_run(invoke_stable_diffusion_xl)


if __name__ == "__main__":
    main_test_sdxl()
