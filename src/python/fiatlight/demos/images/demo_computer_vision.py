import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import lut_channels_in_colorspace
from fiatlight.fiat_kits.fiat_image import image_source
from fiatlight.demos.images.opencv_wrappers import canny, dilate


def main() -> None:
    graph = fl.FunctionsGraph()
    graph.add_function(image_source)

    graph.add_function(lut_channels_in_colorspace)
    graph.add_link("image_source", "lut_channels_in_colorspace")

    graph.add_function_composition([canny, dilate])
    graph.add_link("image_source", "canny")

    fl.fiat_run_graph(graph, app_name="demo_computer_vision")


if __name__ == "__main__":
    main()
