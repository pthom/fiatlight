"""Look-up-table (LUT) wrappers (thin shims over fiat_image).

`lut_with_params` and `lut_channels_in_colorspace` are reused as-is from
`fiatlight.fiat_kits.fiat_image.lut_functions`. They already provide a
`LutParams` BaseModel and a custom GUI editor.
"""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import (
    lut_with_params,
    lut_channels_in_colorspace,
)

fl.add_fiat_attributes(lut_with_params, fiat_tags=["color", "fiat_image"])
fl.add_fiat_attributes(lut_channels_in_colorspace, fiat_tags=["color", "fiat_image"])

__all__ = ["lut_with_params", "lut_channels_in_colorspace"]
