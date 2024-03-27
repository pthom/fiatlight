from fiatlight.demos.images.toon_edges import add_toon_edges, image_source
from fiatlight.demos.images.oil_paint import oil_paint
from fiatlight.demos.ai.stable_diffusion_xl_wrapper import stable_diffusion_xl_gui

from typing import List
from fiatlight.fiat_types import Function
from fiatlight.fiat_core import FunctionWithGuiFactory, to_function_with_gui_factory


def all_functions() -> List[FunctionWithGuiFactory]:
    bare_fn_list: List[Function] = [
        image_source,
        add_toon_edges,
        oil_paint,
    ]
    factories_list = [stable_diffusion_xl_gui]
    r = [to_function_with_gui_factory(f) for f in bare_fn_list] + factories_list
    return r
