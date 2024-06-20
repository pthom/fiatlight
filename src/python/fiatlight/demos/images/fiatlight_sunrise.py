import fiatlight as fl
from fiatlight import fiat_image as fi
import cv2
import numpy as np

# logo_path = fl.demo_assets_dir() + "/logo/logo.jpg"
logo_path = "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/priv_assets/logopxd.jpg"
LOGO_IMG = cv2.imread(logo_path)


@fl.with_fiat_attributes(
    fade_value__range=(0.0, 1.0),
    fade_value__label="Rise and shine!",
)
def fiatlight_sunrise(
    fade_value: float = 0.0,
) -> fi.ImageU8_3:
    image_black = np.zeros_like(LOGO_IMG)
    image = cv2.addWeighted(LOGO_IMG, fade_value, image_black, 1 - fade_value, 0)
    return image


fl.run(fiatlight_sunrise, app_name="Fiatlight")
