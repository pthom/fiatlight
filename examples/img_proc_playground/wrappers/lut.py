"""Look-up-table (LUT) wrappers (thin shims over fiat_image).

`lut_with_params` and `lut_channels_in_colorspace` are reused as-is from
`fiatlight.fiat_kits.fiat_image.lut_functions`. They already provide a
`LutParams` BaseModel and a custom GUI editor.
"""
from fiatlight.fiat_kits.fiat_image import (
    lut_with_params,
    lut_channels_in_colorspace,
)

__all__ = ["lut_with_params", "lut_channels_in_colorspace"]
