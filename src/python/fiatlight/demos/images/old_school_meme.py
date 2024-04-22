import fiatlight
from fiatlight.fiat_image import ImageU8
from fiatlight.fiat_types import Float_0_1, ColorRgb
from typing import NewType

from PIL import Image, ImageDraw, ImageFont
from enum import Enum

import numpy as np
import os


# A synonym for int, but with a font size, between 20 and 100
# (this will create a slider in the GUI)
FontSize = NewType("FontSize", int)
fiatlight.gui_factories().register_bound_int((5, 200), "FontSize")


class MemeFont(Enum):
    Stadium = "fonts/stadium/Stadium.ttf"
    Anton = "fonts/Anton/Anton-Regular.ttf"
    SaoTorpes = "fonts/sao_torpes/SaoTorpes.otf"


fiatlight.gui_factories().register_enum(MemeFont)


def add_meme_text(
    image: ImageU8,
    text: str = "Hello!",
    font_size: FontSize = FontSize(20),
    font_type: MemeFont = MemeFont.Anton,
    x: Float_0_1 = Float_0_1(0.35),
    y: Float_0_1 = Float_0_1(0.75),
    text_color: ColorRgb = (255, 255, 255),  # type: ignore
    outline_color: ColorRgb = (0, 0, 0),  # type: ignore
) -> ImageU8:
    """Add text to an image, with a look that is reminiscent of old-school memes.

    :param image: The image to which the text will be added.
    :param text: The text to add to the image.
    :param font_size: The size of the font.
    :param font_type: The font to use for the text. You can choose between "Stadium", "Anton" and "SaoTorpes".
    :param x: The x position of the text, as a fraction of the image width.
    :param y: The y position of the text, as a fraction of the image height.
    :param text_color: The color of the text.
    :param outline_color: The color of the text outline.

    :return: The image with the text added.
    """

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
        stroke_width=font_size // 10,
        stroke_fill=outline_color_bgr,
        align="center",
    )

    # Convert PIL image to numpy array
    image_with_text = np.array(image_pil)
    return image_with_text  # type: ignore


def sandbox() -> None:
    from fiatlight.demos.ai.stable_diffusion_xl_wrapper import invoke_stable_diffusion_xl
    from fiatlight.fiat_image import image_source

    use_stable_diffusion = False
    if use_stable_diffusion:
        fiatlight.fiat_run_composition([invoke_stable_diffusion_xl, add_meme_text])
    else:
        fiatlight.fiat_run_composition([image_source, add_meme_text])


if __name__ == "__main__":
    sandbox()
