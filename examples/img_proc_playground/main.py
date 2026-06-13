"""Image-processing playground — entry point."""
import fiatlight as fl

from fiatlight.fiat_kits.fiat_image.cv2_nodes import cv2_nodes


def main() -> None:
    params = fl.FiatRunParams()
    # params.theme = fl.ImGuiTheme_.white_is_white
    fl.run_graph_composer(functions=cv2_nodes(), params=params)


if __name__ == "__main__":
    main()
