"""Color-space conversion wrappers (thin shims over fiat_image).

`color_convert` is reused as-is from `fiatlight.fiat_kits.fiat_image.cv_color_type`,
which already exposes a Pydantic `ColorConversion(BaseModel)` with src/dst
color types and runtime validation.
"""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image.cv_color_type import color_convert

fl.add_fiat_attributes(color_convert, fiat_tags=["color", "fiat_image"])

__all__ = ["color_convert"]
