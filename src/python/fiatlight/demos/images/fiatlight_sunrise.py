import fiatlight as fl
from fiatlight import fiat_image as fi
import cv2
import numpy as np

IMAGE_LOGO = cv2.imread("logo.jpg")
IMAGE_BLACK = np.zeros_like(IMAGE_LOGO)


@fl.with_fiat_attributes(fade__range=(0.0, 1.0), label="Rise and shine!")
def fade_image(fade: float = 0.0) -> fi.ImageU8_3:
    return cv2.addWeighted(IMAGE_BLACK, 1 - fade, IMAGE_LOGO, fade, 0)


fl.run(fade_image, app_name="Fiatlight")
