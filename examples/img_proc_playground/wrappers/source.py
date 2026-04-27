"""Image-source wrappers (thin shims over fiat_image).

`image_source` opens an image-picker GUI; `imread_rgb` reads a fixed file
path with correct RGB ordering.
"""
from fiatlight.fiat_kits.fiat_image import image_source, imread_rgb

__all__ = ["image_source", "imread_rgb"]
