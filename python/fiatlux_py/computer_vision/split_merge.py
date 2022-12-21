from typing import Any, Optional, Callable, cast
from fiatlux_py import FunctionWithGui
from fiatlux_py.computer_vision import ImageWithGui, ImageChannelsWithGui, ImageUInt8, ImageFloat
from fiatlux_py.computer_vision.cv_color_type import ColorConversion

import cv2
import numpy as np


def split_channels(image: ImageUInt8) -> ImageUInt8:
    assert len(image.shape) == 3
    depth_first = np.squeeze(np.dsplit(image, image.shape[-1]))
    return depth_first


class SplitChannelsWithGui(FunctionWithGui):
    color_conversion: Optional[ColorConversion] = None
    gui_params_optional_fn: Callable[[], bool]

    def __init__(self) -> None:
        self.input_gui = ImageWithGui()
        self.output_gui = ImageChannelsWithGui()

    def output_gui_channels(self) -> ImageChannelsWithGui:
        return cast(ImageChannelsWithGui, self.output_gui)

    def f(self, x: Any) -> Any:
        assert type(x) == np.ndarray
        if self.color_conversion is not None:
            x_converted = cv2.cvtColor(x, self.color_conversion.conversion_code)
        else:
            x_converted = x
        channels = split_channels(x_converted)
        channels_normalized = channels / 255.0
        return channels_normalized

    def name(self) -> str:
        r = "Split Channels"
        if self.color_conversion is not None:
            r += " - " + self.color_conversion.name
        return r

    def gui_params(self) -> bool:
        if hasattr(self, "gui_params_optional_fn"):
            return self.gui_params_optional_fn()
        else:
            return False


class MergeChannelsWithGui(FunctionWithGui):
    color_conversion: Optional[ColorConversion] = None

    def __init__(self) -> None:
        self.input_gui = ImageChannelsWithGui()
        self.output_gui = ImageWithGui()

    def f(self, x: Any) -> Any:
        assert type(x) == np.ndarray
        channels = [c for c in x]
        image_float = np.dstack(channels)
        image_uint8 = (image_float * 255.0).astype("uint8")
        image_converted = image_uint8
        if self.color_conversion is not None:
            image_converted = cv2.cvtColor(image_uint8, self.color_conversion.conversion_code)
        return image_converted

    def name(self) -> str:
        r = "Merge Channels"
        if self.color_conversion is not None:
            r += " - " + self.color_conversion.name
        return r


