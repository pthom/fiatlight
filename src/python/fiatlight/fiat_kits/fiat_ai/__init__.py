from .prompt import Prompt
from .prompt_with_gui import _register_prompt
from .invoke_sdxl_turbo import invoke_sdxl_turbo
from fiatlight.fiat_types import Function


_register_prompt()


def all_functions() -> list[Function]:
    return [invoke_sdxl_turbo]


__all__ = [
    # from here
    "all_functions",
    # from .prompt
    "Prompt",
    # from .invoke_sdxl_turbo
    "invoke_sdxl_turbo",
]
