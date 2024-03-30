from fiatlight import fiat_run_composition
from fiatlight.fiat_image import ImageU8, lut_channels_in_colorspace
from fiatlight.fiat_types import ImagePath
import cv2


def image_source(image_file: ImagePath) -> ImageU8:
    image = cv2.imread(image_file)
    if image.shape[0] > 1000:
        k = 1000 / image.shape[0]
        image = cv2.resize(image, (0, 0), fx=k, fy=k)
    return image  # type: ignore


def oil_paint(image: ImageU8, size: int = 1, dyn_ratio: int = 3) -> ImageU8:
    return cv2.xphoto.oilPainting(image, size, dyn_ratio, cv2.COLOR_BGR2HSV)  # type: ignore


def main() -> None:
    fiat_run_composition([image_source, lut_channels_in_colorspace, oil_paint])


if __name__ == "__main__":
    main()
