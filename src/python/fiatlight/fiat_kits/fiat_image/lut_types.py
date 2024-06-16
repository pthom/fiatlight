from typing import TypeAlias
from numpy.typing import NDArray
import numpy as np
from fiatlight.fiat_togui.gui_registry import base_model_with_gui_registration
from .cv_color_type import ColorConversion
from pydantic import BaseModel, Field

LutTable: TypeAlias = NDArray[np.uint8]  # an array of 256 elements (LUT, aka Look-Up Table values)


class LutParams(BaseModel):
    """Simple parameters to create a LUT (Look-Up Table) transformation to an image"""

    # LutParams does not use base_model_with_gui_registration,
    # as its gui is specific and implemented in the LutParamsWithGui class.
    pow_exponent: float = 1.0
    min_in: float = 0.0
    min_out: float = 0.0  # <=> 0
    max_in: float = 1.0  # <=> 255
    max_out: float = 1.0

    def to_table(self) -> LutTable:
        x = np.arange(0.0, 1.0, 1.0 / 256.0)
        y = (x - self.min_in) / (self.max_in - self.min_in)
        y = np.clip(y, 0.0, 1.0)
        y = np.power(y, self.pow_exponent)
        y = np.clip(y, 0.0, 1.0)
        y = self.min_out + (self.max_out - self.min_out) * y
        y = np.clip(y, 0.0, 1.0)
        lut_uint8 = (y * 255.0).astype(np.uint8)
        return lut_uint8

    def is_default(self) -> bool:
        return (
            self.pow_exponent == 1.0
            and self.min_in == 0.0
            and self.min_out == 0.0
            and self.max_in == 1.0
            and self.max_out == 1.0
        )


@base_model_with_gui_registration()
class ColorLutParams(BaseModel):
    lut_0: LutParams = Field(default_factory=LutParams)
    lut_1: LutParams = Field(default_factory=LutParams)
    lut_2: LutParams = Field(default_factory=LutParams)
    lut_3: LutParams = Field(default_factory=LutParams)
    lut_color_conversion: ColorConversion | None = None
