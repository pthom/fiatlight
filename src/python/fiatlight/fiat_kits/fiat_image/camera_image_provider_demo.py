from fiatlight.fiat_kits.fiat_image.camera_image_provider import CameraGui
from fiatlight.fiat_kits.fiat_image import ImageU8_3
from fiatlight.demos.images.old_school_meme import add_meme_text
import fiatlight
from pydantic import BaseModel
import cv2


class ImageEffect(BaseModel):
    rotation_degree: int = 0
    flip_horizontal: bool = False
    flip_vertical: bool = False


fiatlight.register_dataclass(ImageEffect)


def apply_image_effect(image: ImageU8_3, effect: ImageEffect | None = None) -> ImageU8_3:
    if effect is None:
        return image
    if effect.rotation_degree != 0:
        height, width = image.shape[:2]
        center = (width / 2, height / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, effect.rotation_degree, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))
    if effect.flip_horizontal:
        image = cv2.flip(image, 1)
    if effect.flip_vertical:
        image = cv2.flip(image, 0)
    return image


def main():
    camera_gui = CameraGui()
    fiatlight.fiat_run_composition([camera_gui, apply_image_effect, add_meme_text])


if __name__ == "__main__":
    main()
