"""Image-source wrappers (thin shims over fiat_image).

`image_source` opens an image-picker GUI; `imread_rgb` reads a fixed file
path with correct RGB ordering.

For shimmed functions we use `add_fiat_attributes` (rather than the
`with_fiat_attributes` decorator) because the function is imported, not
defined here.
"""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import image_source, imread_rgb

fl.add_fiat_attributes(image_source, fiat_tags=["source", "fiat_image"])
fl.add_fiat_attributes(imread_rgb, fiat_tags=["source", "fiat_image"])

__all__ = ["image_source", "imread_rgb"]
