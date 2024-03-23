import fiatlight
from fiatlight.fiat_image import ImageU8, lut_channels_in_colorspace
from fiatlight import fiat_types
import cv2


def image_source(image_file: fiat_types.ImagePath = fiatlight.demo_assets_dir() + "/images/house.jpg") -> ImageU8:  # type: ignore
    image = cv2.imread(image_file)
    if image.shape[0] > 1000:
        k = 1000 / image.shape[0]
        image = cv2.resize(image, (0, 0), fx=k, fy=k)
    return image  # type: ignore


def oil_paint(image: ImageU8, size: int = 1, dyn_ratio: int = 3) -> ImageU8:
    return cv2.xphoto.oilPainting(image, size, dyn_ratio, cv2.COLOR_BGR2HSV)  # type: ignore


def main() -> None:
    functions = [image_source, lut_channels_in_colorspace, oil_paint]
    functions_graph = fiatlight.FunctionsGraph.from_function_composition(functions)  # type: ignore
    fiatlight.fiat_run(functions_graph)


if __name__ == "__main__":
    main()
