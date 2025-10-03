import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8
from fiatlight.fiat_types import ColorRgb

from PIL import Image, ImageDraw, ImageFont
from enum import Enum
from pydantic import BaseModel

import numpy as np
import os


class MemeFont(Enum):
    Stadium = "fonts/stadium/Stadium.ttf"
    Anton = "fonts/Anton/Anton-Regular.ttf"
    SaoTorpes = "fonts/sao_torpes/SaoTorpes.otf"


class MemeTextParams(BaseModel):
    text: str = "Hello!"
    font_size: int = 20
    font_type: MemeFont = MemeFont.Anton
    x: float = 0.35
    y: float = 0.75
    text_color: ColorRgb = ColorRgb((255, 255, 255))  # ------>
    outline_color: ColorRgb = ColorRgb((0, 0, 0))
    is_image_bgr: bool = True


fl.register_base_model(MemeTextParams, x__range=(0, 1), y__range=(0, 1), font_size__range=(5, 100))


@fl.with_fiat_attributes(label="Add Meme Text")
def add_meme_text(image: ImageU8, params: MemeTextParams) -> ImageU8:
    """Add text to an image, with a look that is reminiscent of old-school memes.

    * **image:** The image to which the text will be added.
    * **text:** The text to add to the image.
    * **font_size:** The size of the font.
    * **font_type:** The font to use for the text. You can choose between "Stadium", "Anton" and "SaoTorpes".
    * **x:** The x position of the text, as a fraction of the image width.
    * **y:** The y position of the text, as a fraction of the image height.
    * **text_color:** The color of the text.
    * **outline_color:** The color of the text outline.

    * **return:** The image with the text added.
    """

    image_pil = Image.fromarray(image)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = this_dir + "/" + params.font_type.value
    font = ImageFont.truetype(font_path, params.font_size * 4)

    draw = ImageDraw.Draw(image_pil)

    position = (10, 10)  # Change this to where you want the text to be on the image

    # Argh, OpenCV uses BGR and our color is RGB
    text_color_bgr = (params.text_color[2], params.text_color[1], params.text_color[0])
    outline_color_bgr = (params.outline_color[2], params.outline_color[1], params.outline_color[0])

    # Draw text on image
    # Center it around x, y
    text_size = draw.textbbox(position, params.text, font=font)
    position = (int(params.x * image_pil.width - text_size[0] / 2), int(params.y * image_pil.height - text_size[1] / 2))
    draw.text(
        position,
        params.text,
        font=font,
        fill=text_color_bgr,
        stroke_width=params.font_size // 10,
        stroke_fill=outline_color_bgr,
        align="center",
    )

    # Convert PIL image to numpy array
    image_with_text = np.array(image_pil)
    return image_with_text  # type: ignore


def main() -> None:
    from fiatlight.fiat_kits.fiat_image import image_source

    fl.run([image_source, add_meme_text])


if __name__ == "__main__":
    main()
