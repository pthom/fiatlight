from fiatlight import fiat_run_composition
from fiatlight.fiat_image import ImageU8, lut_channels_in_colorspace
from fiatlight.fiat_image import image_source
import cv2


def oil_paint(image: ImageU8, size: int = 1, dyn_ratio: int = 3) -> ImageU8:
    return cv2.xphoto.oilPainting(image, size, dyn_ratio, cv2.COLOR_BGR2HSV)  # type: ignore


def main() -> None:
    fiat_run_composition([image_source, lut_channels_in_colorspace, oil_paint])


if __name__ == "__main__":
    main()
