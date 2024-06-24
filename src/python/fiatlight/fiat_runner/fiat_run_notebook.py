from fiatlight.fiat_core import FunctionsGraph
from fiatlight.fiat_runner.fiat_gui import FiatGuiParams, FiatGui
from fiatlight.fiat_runner.fiat_gui import get_last_screenshot
from fiatlight.fiat_kits.fiat_image import ImageU8_3
from imgui_bundle import hello_imgui
import imgui_bundle
from typing import Tuple, Optional

ScreenSize = Tuple[int, int]


class NotebookRunnerParams:
    thumbnail_height: int = 0
    thumbnail_ratio: float = 0.5
    run_id: Optional[str] = None


def _fiat_run_graph_nb(
    functions_graph: FunctionsGraph,
    params: FiatGuiParams | None,
    app_name: str | None,
    notebook_runner_params: NotebookRunnerParams | None,
    theme: hello_imgui.ImGuiTheme_ | None = None,
    remember_theme: bool = False,
) -> None:
    "fiatlight runner for jupyter notebook"
    import cv2
    import PIL.Image  # pip install pillow
    from IPython.display import display
    from IPython.core.display import HTML

    if theme is None:
        theme = hello_imgui.ImGuiTheme_.white_is_white

    if notebook_runner_params is None:
        notebook_runner_params = NotebookRunnerParams()

    def run_app() -> None:
        nonlocal notebook_runner_params
        fiat_gui = FiatGui(
            functions_graph, params=params, app_name=app_name, theme=theme, remember_theme=remember_theme
        )
        fiat_gui.run()

    def make_thumbnail(image: ImageU8_3) -> ImageU8_3:
        resize_ratio = 1.0
        if notebook_runner_params.thumbnail_ratio != 0.0:
            resize_ratio = notebook_runner_params.thumbnail_ratio
        elif notebook_runner_params.thumbnail_height > 0:
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

    def display_image(image: ImageU8_3) -> None:
        pil_image = PIL.Image.fromarray(image)
        display(pil_image)  # type: ignore

    def run_app_and_display_thumb() -> None:
        run_app()
        app_image = get_last_screenshot()
        if app_image is None:
            return
        thumbnail = make_thumbnail(app_image)
        display_image(thumbnail)

    def display_run_button() -> None:
        html_code = f"""
        <script>
        function btnClick_{notebook_runner_params.run_id}(btn) {{
            // alert("btnClick_{notebook_runner_params.run_id}");
            cell_element = btn.parentElement.parentElement.parentElement.parentElement.parentElement;
            cell_idx = Jupyter.notebook.get_cell_elements().index(cell_element)
            IPython.notebook.kernel.execute("imgui_bundle.JAVASCRIPT_RUN_ID='{notebook_runner_params.run_id}'")
            Jupyter.notebook.execute_cells([cell_idx])
        }}
        </script>
        <button onClick="btnClick_{notebook_runner_params.run_id}(this)">Run</button>
        """
        display(HTML(html_code))  # type: ignore

    def display_app_with_run_button(run_id: str) -> None:
        """Experiment displaying a "run" button in the notebook below the screenshot. Disabled as of now
        If using this, it would be possible to run the app only if the user clicks on the Run button
        (and not during normal cell execution).
        """
        if run_id is None:
            run_app_and_display_thumb()
        else:
            if hasattr(imgui_bundle, "JAVASCRIPT_RUN_ID"):
                print("imgui_bundle.JAVASCRIPT_RUN_ID=" + imgui_bundle.JAVASCRIPT_RUN_ID + "{run_id=}")
                if imgui_bundle.JAVASCRIPT_RUN_ID == run_id:
                    run_app_and_display_thumb()
            else:
                print("imgui_bundle: no JAVASCRIPT_RUN_ID")

    # display_app_with_run_button(run_id)
    run_app_and_display_thumb()


def display_markdown(md_string: str) -> None:
    from IPython.display import display, Markdown

    display(Markdown(md_string))  # type: ignore
