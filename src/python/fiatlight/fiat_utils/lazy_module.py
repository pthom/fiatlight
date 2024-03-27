from typing import Any


class LazyModule:
    """A class to lazily import a module

    Example usage:

    if TYPE_CHECKING:
        # We do not want to import these modules at startup, since these imports are slow
        import torch  # noqa
        import diffusers  # import   # noqa
        import diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl as pipeline_stable_diffusion_xl  # import StableDiffusionXLPipeline  # noqa
    else:
        torch = LazyModule("torch")
        diffusers = LazyModule("diffusers")
        pipeline_stable_diffusion_xl = LazyModule("diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl")


    And then you can use the module as if it was imported. It will be imported only when needed.
    """

    module_name: str
    module: Any | None

    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.module = None

    def __getattr__(self, name: str) -> Any:
        if self.module is None:
            self.module = __import__(self.module_name)
        return getattr(self.module, name)
