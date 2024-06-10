"""In this example we add a custom presentation function to a function.
We also manually set the limits of a float parameter.

Note: fiatlight include the type `FloatMatrix_Dim1` and `FloatMatrix_Dim2`
      which can be automatically presented as a plot (see example demo_plot_array.py)
"""

import math
import numpy as np
from numpy.typing import NDArray
from imgui_bundle import implot, hello_imgui, ImVec2
from imgui_bundle import immapp

FloatArray = NDArray[np.float64]


def make_range(start: float = 0, stop: float = math.pi * 4, step: float = 0.01) -> FloatArray:
    return np.arange(start, stop, step)


make_range.start__range = (0, 10)  # type: ignore
make_range.stop__range = (0, 10)  # type: ignore


def make_sin(x: FloatArray) -> FloatArray:
    return np.sin(x)


def present_plot_standard(values: FloatArray) -> None:
    """Present the values as a plot using ImPlot.
    In this version we call begin_plot and end_plot manually.
    Inside a node, the plot content will not be draggable or zoomable.
    """
    if implot.begin_plot("Plot", hello_imgui.em_to_vec2(40, 25)):
        implot.plot_line("Values", values)
        implot.end_plot()


plot_size = ImVec2(200, 100)


def present_plot_draggable(values: FloatArray) -> None:
    """Present the values as a plot using ImPlot.
    In this version we use immapp.show_resizable_plot_in_node_editor
    to make the plot content draggable, zoomable and resizable.
    """
    global plot_size

    def plot_function() -> None:
        # If the line below is uncommented, the plot axes will be fixed
        # (and the plot content will be zoomable, but not draggable)
        # implot.setup_axes_limits(0, len(values), -1, 1, imgui.Cond_.always.value)

        implot.plot_line("Values", values)

    plot_size = immapp.show_resizable_plot_in_node_editor("Plot", plot_size, plot_function)


def main() -> None:
    import fiatlight as fl

    graph = fl.FunctionsGraph.from_function_composition([make_range, make_sin])

    # present the output of make_sin as a plot (using the present_plot function)
    graph.function_with_gui_of_name("make_sin").output().set_present_callback(present_plot_draggable)
    # graph.function_with_gui("make_sin").output().set_present_callback(present_plot_standard)

    fl.run(graph)


if __name__ == "__main__":
    main()
