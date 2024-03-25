from fiatlight import FunctionsGraph, fiat_run
from fiatlight.fiat_core import IntWithGui, FloatWithGui
from imgui_bundle import implot, hello_imgui

import numpy as np
from typing import Any, Tuple

# Type aliases for numpy arrays
OneDim = Tuple[Any]  # Synonym for a 1D numpy array
OneDimIntArray = np.ndarray[OneDim, np.dtype[np.int64]]  # Synonym for a 1D numpy array of integers


def random_binomial(n: int = 50, p: float = 0.1) -> OneDimIntArray:
    """
    Make a binomial distribution.

    :param n: Number of trials.
    :param p: Probability of success.
    :return: The binomial distribution.
    """
    r = np.random.binomial(n, p, size=10000)
    return r


def present_histogram(values: OneDimIntArray) -> None:
    if implot.begin_plot("Binomial distribution", hello_imgui.em_to_vec2(40, 25)):
        implot.plot_histogram("Binomial", values, bins=50)
        implot.end_plot()


def main() -> None:
    functions_graph = FunctionsGraph.from_function(random_binomial)

    random_binomial_gui = functions_graph.get_function_with_gui()
    random_binomial_gui.output_of_idx().set_present_custom_callback(present_histogram)

    n_gui = random_binomial_gui.input_as("n", IntWithGui)
    n_gui.params.v_min = 1
    n_gui.params.v_max = 100

    p_gui = random_binomial_gui.input_as("p", FloatWithGui)
    p_gui.params.v_min = 0.0
    p_gui.params.v_max = 1.0

    fiat_run(functions_graph)


if __name__ == "__main__":
    main()
