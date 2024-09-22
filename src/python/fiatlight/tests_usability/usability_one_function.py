import fiatlight as fl
from fiatlight.fiat_kits import fiat_image
from fiatlight.demos.images.toon_edges import add_toon_edges, ToonEdgesParams
import cv2


def toon_2(image_file: fl.fiat_types.ImagePath, params: ToonEdgesParams) -> fiat_image.ImageU8_3:
    image = cv2.imread(image_file)
    r = add_toon_edges(image, params)  # type: ignore
    return r


fl.run(toon_2, app_name="toon_2")
