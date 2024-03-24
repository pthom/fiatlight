import os

import numpy as np

import fiatlight
from fiatlight import FunctionsGraph, fiat_run
from fiatlight.demos.ai.stable_diffusion_xl_wrapper import stable_diffusion_xl_gui
from fiatlight.fiat_image import ImageU8

from fiatlight.fiat_types import Float_0_1, ImagePath, Int_0_100, ColorRgb

import cv2
from PIL import Image, ImageDraw, ImageFont
from enum import Enum


class MemeFont(Enum):
    Stadium = "fonts/stadium/Stadium.ttf"
    Anton = "fonts/anton/Anton-Regular.ttf"
    SaoTorpes = "fonts/sao_torpes/SaoTorpes.otf"


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
    text: str = "Fiat What?",
    font_size: Int_0_100 = 40,  # type: ignore
    font_type: MemeFont = MemeFont.Anton,
    x: Float_0_1 = Float_0_1(0.05),
    y: Float_0_1 = Float_0_1(0.7),
    text_color: ColorRgb = (255, 255, 255),  # type: ignore
    outline_color: ColorRgb = (0, 0, 0),  # type: ignore
) -> ImageU8:
    image_pil = Image.fromarray(image)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = this_dir + "/" + font_type.value
    font = ImageFont.truetype(font_path, font_size * 4)

    draw = ImageDraw.Draw(image_pil)

    position = (10, 10)  # Change this to where you want the text to be on the image

    # Argh, OpenCV uses BGR and our color is RGB
    text_color_bgr = (text_color[2], text_color[1], text_color[0])
    outline_color_bgr = (outline_color[2], outline_color[1], outline_color[0])

    # Draw text on image
    # Center it around x, y
    text_size = draw.textbbox(position, text, font=font)
    position = (int(x * image_pil.width - text_size[0] / 2), int(y * image_pil.height - text_size[1] / 2))
    draw.text(
        position,
        text,
        font=font,
        fill=text_color_bgr,
        stroke_width=2,
        stroke_fill=outline_color_bgr,
        align="center",
    )

    # Convert PIL image to numpy array
    image_with_text = np.array(image_pil)
    return image_with_text


def main() -> None:
    graph = FunctionsGraph.from_function_composition(
        [stable_diffusion_xl_gui(), add_meme_text],
        # [image_source, add_meme_text],
        locals_dict=locals(),
        globals_dict=globals(),
    )

    fiat_run(graph)


if __name__ == "__main__":
    main()
