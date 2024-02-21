from typing import Tuple, TypeAlias
from numpy.typing import NDArray
import cv2
import numpy as np
from fiatlight.computer_vision import ImageUInt8


LutTable: TypeAlias = NDArray[np.uint8]


class LutParams:
    pow_exponent: float = 1.0
    min_in: float = 0.0
    min_out: float = 0.0  # <=> 0
    max_in: float = 1.0  # <=> 255
    max_out: float = 1.0


def lut_params_to_table(params: LutParams) -> LutTable:
    x = np.arange(0.0, 1.0, 1.0 / 256.0)
    y = (x - params.min_in) / (params.max_in - params.min_in)
    y = np.clip(y, 0.0, 1.0)
    y = np.power(y, params.pow_exponent)
    y = np.clip(y, 0.0, 1.0)
    y = params.min_out + (params.max_out - params.min_out) * y
    y = np.clip(y, 0.0, 1.0)
    lut_uint8 = (y * 255.0).astype(np.uint8)
    return lut_uint8


# def apply_lut_to_float01_image(image: ImageFloat, lut_table: LutTable) -> ImageFloat:
#     image_uint8: ImageUInt8 = (image * 255.0).astype(np.uint8)
#     image_with_lut_uint8 = np.zeros_like(image_uint8)
#     cv2.LUT(image_uint8, lut_table, image_with_lut_uint8)
#     image_adjusted: ImageFloat = image_with_lut_uint8.astype(float) / 255.0
#     return image_adjusted


def apply_lut_to_uint8_image(image: ImageUInt8, lut_table: LutTable) -> ImageUInt8:
    # image_with_lut_uint8 = np.zeros_like(image)
    # cv2.LUT(image, lut_table, image_with_lut_uint8)
    image_with_lut_uint8 = cv2.LUT(image, lut_table)
    return image_with_lut_uint8  # type: ignore


def present_lut_table(lut_table: LutTable, size: int) -> ImageUInt8:
    from imgui_bundle import immvision

    image = np.zeros((size, size, 4), dtype=np.uint8)
    assert len(lut_table) == 256

    def to_point(x: float, y: float) -> Tuple[float, float]:
        return 1.0 + x * (size - 3), 1.0 + (1.0 - y) * (size - 3)

    y = lut_table.astype(np.float_) / 255.0
    x = np.arange(0.0, 1.0, 1.0 / 256.0)

    image[:, :, :] = (200, 200, 200, 0)
    color = (0, 255, 255, 255)
    for i in range(255):
        x0, y0 = float(x[i]), float(y[i])
        x1, y1 = float(x[i + 1]), float(y[i + 1])
        immvision.cv_drawing_utils.line(image, to_point(x0, y0), to_point(x1, y1), color)
    return image
