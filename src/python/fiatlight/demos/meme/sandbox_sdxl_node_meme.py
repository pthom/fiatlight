import os

import numpy as np

import fiatlight
from fiatlight import FunctionsGraph, fiat_run
from fiatlight.fiat_image import ImageU8

from fiatlight.fiat_types import Float_0_1, ImagePath, Int_0_255
from typing import Tuple

import cv2
from PIL import Image, ImageDraw, ImageFont
from enum import Enum


class MemeFont(Enum):
    SaoTorpes = "fonts/sao_torpes/SaoTorpes.otf"
    WallShaker = "fonts/wall_shaker/WallShaker.ttf"
    Stadium = "fonts/stadium/Stadium.ttf"


def image_source(image_file: ImagePath = fiatlight.demo_assets_dir() + "/images/house.jpg") -> ImageU8:  # type: ignore
    image = cv2.imread(image_file)
    if image.shape[0] > 1000:
        k = 1000 / image.shape[0]
        image = cv2.resize(image, (0, 0), fx=k, fy=k)
    return image  # type: ignore


def oil_paint(image: ImageU8, size: int = 1, dynRatio: int = 3) -> ImageU8:
    """Applies oil painting effect to an image, using the OpenCV xphoto module."""
    return cv2.xphoto.oilPainting(image, size, dynRatio, cv2.COLOR_BGR2HSV)  # type: ignore


def add_meme_text(
    image: ImageU8,
    text: str = "Hello, World!",
    font_size: Int_0_255 = 120,
    font: MemeFont = MemeFont.Stadium,
    x: Float_0_1 = Float_0_1(0.5),
    y: Float_0_1 = Float_0_1(0.5),
    color: Tuple[int, int, int] = (255, 255, 255),
) -> ImageU8:
    # text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_size, 2)[0]
    # text_x = int((image.shape[1] - text_size[0]) * x)
    # text_y = int((image.shape[0] + text_size[1]) * y)
    # image_copy = image.copy()
    # cv2.putText(image_copy, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 2)
    # return image_copy
    return image

    image_pil = Image.fromarray(image)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = this_dir + "/fonts"
    font_path = font_dir + "/" + font.value
    font = ImageFont.truetype(font_path, font_size)

    draw = ImageDraw.Draw(image_pil)

    position = (10, 10)  # Change this to where you want the text to be on the image

    # Optional: Text color and outline
    text_color = "white"
    outline_color = "black"

    # Draw text on image
    draw.text(position, text, fill=text_color, font=font, stroke_width=2, stroke_fill=outline_color)

    # Convert PIL image to numpy array
    image_with_text = np.array(image_pil)
    return image_with_text


def main() -> None:
    graph = FunctionsGraph.from_function_composition(
        # [stable_diffusion_xl_gui(), fiat_image.lut_channels_in_colorspace, add_toon_edges, oil_paint]
        [image_source, add_meme_text]
    )

    fiat_run(graph)


if __name__ == "__main__":
    main()
