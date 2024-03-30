from fiatlight.demos.ai.stable_diffusion_xl_wrapper import invoke_stable_diffusion_xl
from fiatlight.fiat_types import Function

from typing import List


def all_functions() -> List[Function]:
    return [invoke_stable_diffusion_xl]


__all__ = ["all_functions", "invoke_stable_diffusion_xl"]
