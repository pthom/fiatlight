import numpy as np
import math
from typing import Any, Tuple


# Type aliases for numpy arrays
OneDim = Tuple[Any]  # Synonym for a 1D numpy array
OneDimFloatArray = np.ndarray[OneDim, np.dtype[np.float64]]  # Synonym for a 1D numpy array of floats


def make_range(start: float = 0, stop: float = math.pi * 4, step: float = 0.01) -> OneDimFloatArray:
    return np.arange(start, stop, step)


def make_sin(x: OneDimFloatArray) -> OneDimFloatArray:
    return np.sin(x)


def present_plot(values: OneDimFloatArray) -> None:
    from imgui_bundle import implot, hello_imgui, imgui

    implot.set_next_axes_limits(0, len(values), -1, 1, imgui.Cond_.always.value)
    if implot.begin_plot("Plot", hello_imgui.em_to_vec2(40, 25)):
        implot.plot_line("Values", values)
        implot.end_plot()


def main() -> None:
    from fiatlight import FunctionsGraph, fiat_run

    graph = FunctionsGraph.from_function_composition([make_range, make_sin])

    # present the output of make_sin as a plot (using the present_plot function)
    graph.function_with_gui("make_sin").output().set_present_custom_callback(present_plot)
    # set the range of the stop parameter of make_range to 100
    graph.function_with_gui("make_range").input_as_float("stop").params.v_max = 100

    fiat_run(graph)


if __name__ == "__main__":
    main()
