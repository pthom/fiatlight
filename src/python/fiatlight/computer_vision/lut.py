from typing import Tuple, TypeAlias
from numpy.typing import NDArray
import cv2
import numpy as np
from fiatlight.computer_vision import ImageUInt8


LutTable: TypeAlias = NDArray[np.uint8]  # an array of 256 elements (LUT, aka Look-Up Table values)


class LutParams:
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


def lut_with_params(image: ImageUInt8, params: LutParams) -> ImageUInt8:
    r = lut(image, params.to_table())
    return r


def lut_channels_with_params(
    image: ImageUInt8,
    lut_channel_0: LutParams,
    lut_channel_1: LutParams | None = None,
    lut_channel_2: LutParams | None = None,
    lut_channel_3: LutParams | None = None,
) -> ImageUInt8:
    lut_channel_1 = lut_channel_1 or lut_channel_0
    lut_channel_2 = lut_channel_2 or lut_channel_0
    lut_channel_3 = lut_channel_3 or lut_channel_0
    lut_params = [lut_channel_0, lut_channel_1, lut_channel_2, lut_channel_3]
    if len(image.shape) == 2:
        return lut_with_params(image, lut_params[0])
    nb_channels = image.shape[2]
    channels = cv2.split(image)
    assert len(channels) == nb_channels
    result_channels = [lut_with_params(channels[i], lut_params[i]) for i in range(nb_channels)]
    result = cv2.merge(result_channels)
    return result


def lut(image: ImageUInt8, lut_table: LutTable) -> ImageUInt8:
    assert len(lut_table) == 256
    image_with_lut_uint8 = cv2.LUT(image, lut_table)
    return image_with_lut_uint8  # type: ignore


def lut_table_graph(lut_table: LutTable, size: int) -> ImageUInt8:
    """A small image representing the LUT table."""
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
