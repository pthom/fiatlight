"""Image-processing playground — entry point."""
import fiatlight as fl

from examples.img_proc_playground.wrappers import all_opencv_wrappers


def main() -> None:
    params = fl.FiatRunParams()
    # params.theme = fl.ImGuiTheme_.white_is_white
    fl.run_graph_composer(functions=all_opencv_wrappers(), params=params)


if __name__ == "__main__":
    main()
