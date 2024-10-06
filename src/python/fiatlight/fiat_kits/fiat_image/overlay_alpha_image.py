from fiatlight.fiat_kits.fiat_image.image_types import ImageRgb, ImageRgba
from fiatlight.fiat_utils import with_fiat_attributes

import numpy as np


@with_fiat_attributes(alpha__range=(0.0, 1.0), gamma_factor__range=(0.0, 3.0))
def overlay_alpha_image(
    background_rgb: ImageRgb,
    overlay_rgba: ImageRgba,
    alpha: float = 1.0,
    gamma_factor: float = 2.2,
) -> ImageRgb:
    """
    cf minute physics brilliant clip "Computer color is broken" : https://www.youtube.com/watch?v=LKnqECcg6Gw
    the RGB values are gamma-corrected by the sensor (in order to keep accuracy for lower luminance),
    we need to undo this before averaging.
    """
    overlay_alpha = overlay_rgba[:, :, 3].astype(float) / 255.0 * alpha
    overlay_alpha_3 = np.dstack((overlay_alpha, overlay_alpha, overlay_alpha))

    overlay_rgb_squared = np.float_power(overlay_rgba[:, :, :3].astype(float), gamma_factor)
    background_rgb_squared = np.float_power(background_rgb.astype(float), gamma_factor)
    out_rgb_squared = overlay_rgb_squared * overlay_alpha_3 + background_rgb_squared * (1.0 - overlay_alpha_3)
    out_rgb = np.float_power(out_rgb_squared, 1.0 / gamma_factor)
    out_rgb = out_rgb.astype(np.uint8)
    return out_rgb  # type: ignore
