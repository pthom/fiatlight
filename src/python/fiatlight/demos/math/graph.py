from fiatlight import FunctionsGraph, fiat_run
from imgui_bundle import implot, hello_imgui, imgui_knobs

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


def edit_probability(p: float) -> [bool, float]:
    changed, p = imgui_knobs.knob("Probability", p, 0.0, 1.0)
    return changed, p


def edit_n(n: int) -> [bool, int]:
    changed, n = imgui_knobs.knob("Number of trials", n, 1, 100)
    return changed, n


def main() -> None:
    functions_graph = FunctionsGraph.from_function(random_binomial)

    random_binomial_gui = functions_graph.get_function_with_gui()
    random_binomial_gui.output_of_idx().set_present_custom_callback(present_histogram)

    random_binomial_gui.input_of_name("p").set_edit_callback(edit_probability)
    random_binomial_gui.input_of_name("n").set_edit_callback(edit_n)

    fiat_run(functions_graph)


if __name__ == "__main__":
    main()
