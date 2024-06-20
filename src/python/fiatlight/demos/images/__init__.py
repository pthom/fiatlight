from fiatlight.fiat_kits.fiat_image.overlay_alpha_image import overlay_alpha_image
from fiatlight.demos.images.toon_edges import add_toon_edges
from fiatlight.fiat_kits.fiat_image import image_source
from fiatlight.fiat_types import FunctionList


def all_functions() -> FunctionList:
    from fiatlight.demos.images.opencv_wrappers import all_functions as all_opencv_image_functions

    r = all_opencv_image_functions + [
        image_source,
        # Other
        add_toon_edges,
        overlay_alpha_image,
    ]
    return r  # type: ignore


__all__ = ["all_functions", "overlay_alpha_image", "add_toon_edges", "opencv_wrappers"]
