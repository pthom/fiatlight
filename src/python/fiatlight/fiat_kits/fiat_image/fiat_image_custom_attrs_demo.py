import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8_3
import cv2


demo_image: ImageU8_3 = cv2.imread(fl.demo_assets_dir() + "/images/house.jpg")  # type: ignore


def show_image(image: ImageU8_3 = demo_image) -> ImageU8_3:
    return image


@fl.with_custom_attrs(return__image_display_size=(0, 200), return__show_channels=True, return__zoom_key="a")
def show_image_2(image: ImageU8_3 = demo_image) -> ImageU8_3:
    return image


def main() -> None:
    graph = fl.FunctionsGraph()
    # graph.add_function(show_image)
    graph.add_function(show_image_2)

    fl.fiat_run_graph(graph, app_name="Image Custom Attributes Demo")


if __name__ == "__main__":
    main()
