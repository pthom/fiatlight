from fiatlight.fiat_kits.fiat_image.overlay_alpha_image import overlay_alpha_image
from fiatlight.demos.images.toon_edges import add_toon_edges
from fiatlight.fiat_kits.fiat_image import image_from_file_resized
from fiatlight.fiat_types import FunctionList


def all_functions() -> FunctionList:
    from fiatlight.fiat_kits.fiat_image.cv2_nodes import Canny, dilate, oil_paint

    r = [
        Canny,
        dilate,
        oil_paint,
        image_from_file_resized,
        # Other
        add_toon_edges,
        overlay_alpha_image,
    ]
    return r  # type: ignore


__all__ = ["all_functions", "overlay_alpha_image", "add_toon_edges"]
