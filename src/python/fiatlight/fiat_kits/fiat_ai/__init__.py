from .prompt import Prompt
from .prompt_with_gui import _register_prompt
from .invoke_sdxl_turbo import invoke_sdxl_turbo
from fiatlight.fiat_types import Function


_register_prompt()


def ai_nodes() -> list[Function]:
    """The AI node pack (currently the SDXL-turbo image generator).

    Heavy (imports torch, GPU/network-bound), so it is opt-in: not part of the
    default `fl.studio()` palette.
    """
    return [invoke_sdxl_turbo]


__all__ = [
    # from here
    "ai_nodes",
    # from .prompt
    "Prompt",
    # from .invoke_sdxl_turbo
    "invoke_sdxl_turbo",
]
