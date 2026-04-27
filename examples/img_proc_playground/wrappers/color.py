"""Color-space conversion wrappers (thin shims over fiat_image).

`color_convert` is reused as-is from `fiatlight.fiat_kits.fiat_image.cv_color_type`,
which already exposes a Pydantic `ColorConversion(BaseModel)` with src/dst
color types and runtime validation.
"""
from fiatlight.fiat_kits.fiat_image.cv_color_type import color_convert

__all__ = ["color_convert"]
