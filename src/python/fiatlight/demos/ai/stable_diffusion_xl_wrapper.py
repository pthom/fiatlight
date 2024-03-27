import fiatlight
from fiatlight.fiat_image import ImageU8
from fiatlight.fiat_utils import LazyModule

import numpy as np
from enum import Enum
import cv2


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


#
# def _late_imports() -> None:
#     # mypy: disable-error-code="no-untyped-call"
#     from diffusers import AutoPipelineForText2Image  # noqa
#     from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline  # noqa
#     import torch  # noqa


class InferenceDeviceType(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


_INFERENCE_DEVICE_TYPE = InferenceDeviceType.MPS


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


def stable_diffusion_xl(
    prompt: str,
    seed: int = 42,
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
    # return _stable_diffusion_xl_wrapper.query(prompt, seed, num_inference_steps, guidance_scale)


def stable_diffusion_xl_gui() -> fiatlight.FunctionWithGui:
    """Convert stable_diffusion_xl to a function with GUI,
    then customize min / max values for the input parameters in the GUI of the stable_diffusion_xl node
    """
    stable_diffusion_xl_gui = fiatlight.to_function_with_gui(stable_diffusion_xl)
    # Do not invoke automatically, since the image creation can be slow (about 1 second)
    stable_diffusion_xl_gui.invoke_automatically = False
    stable_diffusion_xl_gui.invoke_automatically_can_set = False

    prompt_input = stable_diffusion_xl_gui.input("prompt")
    assert isinstance(prompt_input, fiatlight.fiat_core.StrWithGui)
    prompt_input.params.edit_type = fiatlight.fiat_core.StrEditType.multiline
    prompt_input.params.width_em = 60

    return stable_diffusion_xl_gui


if __name__ == "__main__":
    graph = fiatlight.FunctionsGraph.from_function_composition([stable_diffusion_xl_gui()])
    fiatlight.fiat_run(graph)
