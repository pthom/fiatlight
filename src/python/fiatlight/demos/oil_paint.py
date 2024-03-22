import fiatlight
from fiatlight.computer_vision import ImageUInt8, lut_channels_in_colorspace
from fiatlight import ImagePath
import cv2


def image_source(image_file: ImagePath = fiatlight.demo_assets_dir() + "/images/house.jpg") -> ImageUInt8:  # type: ignore
    image = cv2.imread(image_file)
    if image.shape[0] > 1000:
        k = 1000 / image.shape[0]
        image = cv2.resize(image, (0, 0), fx=k, fy=k)
    return image  # type: ignore


def oil_paint(image: ImageUInt8, size: int = 1, dyn_ratio: int = 3) -> ImageUInt8:
    return cv2.xphoto.oilPainting(image, size, dyn_ratio, cv2.COLOR_BGR2HSV)  # type: ignore


def main() -> None:
    functions = [image_source, lut_channels_in_colorspace, oil_paint]
    functions_graph = fiatlight.FunctionsGraph.from_function_composition(functions)  # type: ignore
    fiatlight.fiat_run(functions_graph)


if __name__ == "__main__":
    main()
