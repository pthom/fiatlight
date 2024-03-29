from typing import Any
from fiatlight import FunctionWithGui, FunctionParameterWithGui
from fiatlight.computer_vision import ImageUInt8, Image
from fiatlight.computer_vision.image_with_gui import ImageWithGui, ImageChannelsWithGui
from fiatlight.computer_vision import cv_color_type, cv_color_type_gui

import numpy as np


def split_channels(image: ImageUInt8) -> ImageUInt8:
    assert len(image.shape) == 3
    depth_first = np.squeeze(np.dsplit(image, image.shape[-1]))
    return depth_first


class SplitChannelsWithGui(FunctionWithGui[Image, Image]):
    def __init__(self) -> None:
        self.input_gui = ImageWithGui()
        self.output_gui = ImageChannelsWithGui()
        self.name = "Split Channels"

        def f(x: Any) -> Any:
            assert type(x) == np.ndarray
            channels = split_channels(x)
            return channels

        self.f_impl = f


class MergeChannelsWithGui(FunctionWithGui[Image, Image]):
    def __init__(self) -> None:
        self.input_gui = ImageChannelsWithGui()
        self.output_gui = ImageWithGui()
        self.name = "Merge Channels"

        def f(x: Any) -> Any:
            assert type(x) == np.ndarray
            channels = [c for c in x]
            image_stacked = np.dstack(channels)
            # image_uint8 = (image_stacked * 255.0).astype("uint8")
            return image_stacked

        self.f_impl = f


class ConvertColorWithGui(FunctionWithGui[ImageUInt8, ImageUInt8]):
    color_conversion_with_gui: cv_color_type_gui.ConvertColorWithGui
    input_gui: ImageWithGui
    output_gui: ImageWithGui

    def __init__(self, color_conversion: cv_color_type.ColorConversion | None = None) -> None:
        self.color_conversion_with_gui = cv_color_type_gui.ConvertColorWithGui(color_conversion)
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()
        self.name = "Convert Color"

        def f(x: Any) -> Any:
            if x is None or self.color_conversion_with_gui.value is None:
                return None
            r = self.color_conversion_with_gui.value.convert_image(x)
            self.output_gui.color_type = self.color_conversion_with_gui.value.dst_color
            self.output_gui.refresh_image()
            return r

        self.f_impl = f
        self.parameters_with_gui = [FunctionParameterWithGui("color_conversion", self.color_conversion_with_gui)]
