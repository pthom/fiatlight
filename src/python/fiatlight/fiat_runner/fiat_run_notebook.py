from fiatlight.fiat_core import FunctionsGraph
from fiatlight.fiat_runner.fiat_gui import FiatRunParams, FiatGui
from fiatlight.fiat_runner.fiat_gui import get_last_screenshot
from fiatlight.fiat_kits.fiat_image import ImageRgb
from imgui_bundle import hello_imgui, immapp
from typing import Tuple, Optional

ScreenSize = Tuple[int, int]


class NotebookRunnerParams:
    thumbnail_height: int | None = None
    thumbnail_ratio: float | None = None
    run_id: Optional[str] = None


def _fiat_run_graph_nb(
    functions_graph: FunctionsGraph,
    params: FiatRunParams,
    notebook_runner_params: NotebookRunnerParams | None,
) -> None:
    "fiatlight runner for jupyter notebook"
    import cv2
    import PIL.Image  # pip install pillow
    from IPython.display import display

    # Restore the original C++ run method if it was replaced by
    # imgui_bundle's notebook_do_patch_runners_if_needed (which adds a screenshot feature)
    # we are providing here our own implementation of the screenshot.
    if hasattr(immapp, "run_original"):
        immapp.run = immapp.run_original
        del immapp.run_original

    if params.theme is None:
        params.theme = hello_imgui.ImGuiTheme_.white_is_white

    if notebook_runner_params is None:
        notebook_runner_params = NotebookRunnerParams()

    def run_app() -> None:
        nonlocal notebook_runner_params
        fiat_gui = FiatGui(
            functions_graph,
            params=params,
        )
        fiat_gui.run()

    def make_thumbnail(image: ImageRgb) -> ImageRgb:
        resize_ratio = 1.0
        if notebook_runner_params.thumbnail_ratio is not None:
            resize_ratio = notebook_runner_params.thumbnail_ratio
        elif notebook_runner_params.thumbnail_height is not None:
            resize_ratio = notebook_runner_params.thumbnail_height / image.shape[0]

        if resize_ratio != 1:
            if image.shape[0] == 0 or image.shape[1] == 0:
                raise ValueError(
                    "cannot store thumbnail! Make sure that all nodes are visible before exiting the app, so that a screenshot can be taken."
                )
            thumbnail_image = cv2.resize(
                image,
                (0, 0),
                fx=resize_ratio,
                fy=resize_ratio,
                interpolation=cv2.INTER_AREA,
            )
        else:
            thumbnail_image = image
        return thumbnail_image  # type: ignore

    def display_image(image: ImageRgb) -> None:
        pil_image = PIL.Image.fromarray(image)
        display(pil_image)  # type: ignore

    def run_app_and_display_thumb() -> None:
        run_app()
        app_image = get_last_screenshot()
        scale = hello_imgui.final_app_window_screenshot_framebuffer_scale()
        if notebook_runner_params.thumbnail_ratio is None:
            notebook_runner_params.thumbnail_ratio = 1.0 / scale
        if app_image is None:
            return
        thumbnail = make_thumbnail(app_image)
        display_image(thumbnail)

    run_app_and_display_thumb()


def display_markdown(md_string: str) -> None:
    from IPython.display import display, Markdown

    display(Markdown(md_string))  # type: ignore
