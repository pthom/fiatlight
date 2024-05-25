from fiatlight.demos.images import add_meme_text
from fiatlight.fiat_kits.fiat_image.camera_image_provider import CameraImageProviderGui
from fiatlight.fiat_kits.fiat_image import ImageU8_3
import fiatlight
from pydantic import BaseModel
import cv2
from typing import Optional

fiatlight.get_fiat_config().catch_function_exceptions = False


@fiatlight.base_model_with_gui_registration(rotation_degree__range=(0, 360))
class ImageEffect(BaseModel):
    rotation_degree: int = 0
    flip_horizontal: bool = False
    flip_vertical: bool = False


def apply_image_effect(image: ImageU8_3, effect: Optional[ImageEffect] = None) -> ImageU8_3:
    if effect is None:
        return image
    if effect.rotation_degree != 0:
        height, width = image.shape[:2]
        center = (width / 2, height / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, effect.rotation_degree, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))  # type: ignore
    if effect.flip_horizontal:
        image = cv2.flip(image, 1)  # type: ignore
    if effect.flip_vertical:
        image = cv2.flip(image, 0)  # type: ignore
    return image


def main() -> None:
    camera_gui = CameraImageProviderGui()
    fiatlight.fiat_run_composition([camera_gui, apply_image_effect, add_meme_text])


if __name__ == "__main__":
    main()
