"""Image processors: _example_ of a collection of image processors
An ImageProcessor is simply a class that can transform an image into another image, with internal parameters.

ImageEffect is an ImageProcessor that groups several other processors,
and which can be used to apply multiple transformations to an image.

Technical notes:
    - all the processors are implemented as Pydantic models, which allows to easily serialize/deserialize them
    - the processors are registered with the GUI, so that they can be easily used in a GUI application
    - ImageEffect contains multiple nested BaseModel: this will be nicely handled by the GUI
"""

from fiatlight import fiat_image as fi
from fiatlight.fiat_kits.fiat_image.add_meme_text import add_meme_text, MemeTextParams
import fiatlight as fl

from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Optional
import cv2
import numpy as np


class ImageProcessor(BaseModel, ABC):
    """Base class for image processors."""

    @abstractmethod
    def process(self, image: fi.ImageRgb) -> fi.ImageRgb:
        pass


@fl.base_model_with_gui_registration(
    rot_degree__range=(0, 360),
    rot_degree__edit_type="knob",
    flip_v__edit_type="toggle",
    flip_h__edit_type="toggle",
)
class GeometricTransformation(ImageProcessor):
    """Geometric transformation of an image (rotation, flip)."""

    rot_degree: int = 0
    flip_h: bool = False
    flip_v: bool = False

    def process(self, image: fi.ImageRgb) -> fi.ImageRgb:
        if self.rot_degree != 0:
            height, width = image.shape[:2]
            center = (width / 2, height / 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, self.rot_degree, 1.0)
            image = cv2.warpAffine(image, rotation_matrix, (width, height))  # type: ignore
        if self.flip_h:
            image = cv2.flip(image, 1)  # type: ignore
        if self.flip_v:
            image = cv2.flip(image, 0)  # type: ignore
        return image


@fl.base_model_with_gui_registration()
class ColorProcessing(ImageProcessor):
    """Color processing of an image (LUT curves on channels, with an option color conversion in between)"""

    lut_0: Optional[fi.LutParams] = None
    lut_1: Optional[fi.LutParams] = None
    lut_2: Optional[fi.LutParams] = None
    lut_3: Optional[fi.LutParams] = None
    src_color: fi.ColorType = fi.ColorType.BGR
    lut_color: fi.ColorType = fi.ColorType.HSV

    def process(self, image: fi.ImageRgb) -> fi.ImageRgb:
        image_color_conversion_1 = fi.ColorConversion(src_color=self.src_color, dst_color=self.lut_color)
        image_color_conversion_2 = fi.ColorConversion(src_color=self.lut_color, dst_color=self.src_color)
        image_color = image_color_conversion_1.convert_image(image)
        image_color_lut = fi.lut_channels_with_params(image_color, self.lut_0, self.lut_1, self.lut_2, self.lut_3)
        image_lut = image_color_conversion_2.convert_image(image_color_lut)
        return image_lut  # type: ignore


@fl.base_model_with_gui_registration(
    blur_radius__range=(0.0, 10.0),
    sharpen__edit_type="toggle",
)
class ImageFilters(BaseModel):
    blur_radius: float = 0.0
    sharpen: bool = False

    def process(self, image: fi.ImageRgb) -> fi.ImageRgb:
        if self.blur_radius:
            image = cv2.GaussianBlur(image, (0, 0), self.blur_radius)  # type: ignore
        if self.sharpen:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            image = cv2.filter2D(image, -1, kernel)  # type: ignore
        return image


@fl.base_model_with_gui_registration()
class AddTitleOnImage(ImageProcessor):
    params: MemeTextParams

    def process(self, image: fi.ImageRgb) -> fi.ImageRgb:
        return add_meme_text(image, self.params)  # type: ignore


@fl.base_model_with_gui_registration(
    edit_detachable=True,
)
class ImageEffect(BaseModel):
    geo_transf: Optional[GeometricTransformation] = None
    color_filter: Optional[ColorProcessing] = None
    image_filters: Optional[ImageFilters] = None
    title_text: Optional[AddTitleOnImage] = None

    def process(self, image: fi.ImageRgb) -> fi.ImageRgb:
        if self.geo_transf:
            image = self.geo_transf.process(image)
        if self.color_filter:
            image = self.color_filter.process(image)
        if self.image_filters:
            image = self.image_filters.process(image)
        if self.title_text:
            image = self.title_text.process(image)
        return image


def apply_image_effect(image: fi.ImageRgb, effect: ImageEffect) -> fi.ImageRgb:
    return effect.process(image)
