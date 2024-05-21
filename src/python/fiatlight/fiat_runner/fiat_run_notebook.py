from fiatlight.fiat_core import FunctionsGraph
from fiatlight.fiat_runner.fiat_gui import FiatGuiParams, FiatGui
from fiatlight.fiat_runner.fiat_gui import get_last_screenshot
import imgui_bundle
from typing import Callable, Tuple, Optional

VoidFunction = Callable[[], None]
ScreenSize = Tuple[int, int]


class NotebookRunnerParams:
    thumbnail_height: int = 0
    thumbnail_ratio: float = 0.5
    run_id: Optional[str] = None


def _fiat_run_graph_nb(
    functions_graph: FunctionsGraph,
    params: FiatGuiParams | None,
    notebook_runner_params: NotebookRunnerParams | None,
) -> None:
    "fiatlight runner for jupyter notebook"
    import cv2  # type: ignore
    import PIL.Image  # pip install pillow
    from IPython.display import display  # type: ignore
    from IPython.core.display import HTML  # type: ignore

    if notebook_runner_params is None:
        notebook_runner_params = NotebookRunnerParams()

    def run_app():
        nonlocal notebook_runner_params
        # @immapp.static(was_theme_set=False)
        # def gui_with_light_theme():
        #     static = gui_with_light_theme
        #     if not static.was_theme_set:
        #         hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.white_is_white)
        #         static.was_theme_set = True
        #     gui_function()

        fiat_gui = FiatGui(functions_graph, params)
        fiat_gui.run()

    def make_thumbnail(image):
        resize_ratio = 1.0
        if notebook_runner_params.thumbnail_ratio != 0.0:
            resize_ratio = notebook_runner_params.thumbnail_ratio
        elif notebook_runner_params.thumbnail_height > 0:
            resize_ratio = notebook_runner_params.thumbnail_height / image.shape[0]

        if resize_ratio != 1:
            thumbnail_image = cv2.resize(
                image,
                (0, 0),
                fx=resize_ratio,
                fy=resize_ratio,
                interpolation=cv2.INTER_AREA,
            )
        else:
            thumbnail_image = image
        return thumbnail_image

    def display_image(image):
        pil_image = PIL.Image.fromarray(image)
        display(pil_image)

    def run_app_and_display_thumb():
        run_app()
        app_image = get_last_screenshot()
        thumbnail = make_thumbnail(app_image)
        display_image(thumbnail)

    def display_run_button():
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
        display(HTML(html_code))

    def display_app_with_run_button(run_id):
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
