import numpy as np

import fiatlight
from imgui_bundle import implot, hello_imgui
from typing import Any, Tuple

OneDim = Tuple[Any]  # Synonym for a 1D numpy array


def random_binomial(n: int = 50, p: float = 0.1) -> np.ndarray[OneDim, np.dtype[np.int64]]:
    """
    Make a binomial distribution.

    :param n: Number of trials.
    :param p: Probability of success.
    :return: The binomial distribution.
    """
    r = np.random.binomial(n, p, size=10000)
    return r


def manual_debug() -> None:
    n = 10
    p = 0.5
    r = random_binomial(n, p)
    print(r)


def with_gui() -> None:
    from fiatlight import FunctionsGraph, fiat_run

    random_binomial_gui = fiatlight.to_function_with_gui(random_binomial)

    binomial_output = random_binomial_gui.outputs_with_gui[0]

    def present_custom() -> None:
        value = binomial_output.data_with_gui.get_actual_value()
        if implot.begin_plot("Binomial distribution", hello_imgui.em_to_vec2(40, 25)):
            implot.plot_histogram("Binomial", value, bins=50)
            implot.end_plot()

    random_binomial_gui.outputs_with_gui[0].data_with_gui.callbacks.present_custom = present_custom

    n_gui = random_binomial_gui.input_of_name("n")
    assert isinstance(n_gui, fiatlight.fiat_core.IntWithGui)
    n_gui.params.v_min = 1
    n_gui.params.v_max = 100

    p_gui = random_binomial_gui.input_of_name("p")
    assert isinstance(p_gui, fiatlight.fiat_core.FloatWithGui)
    p_gui.params.v_min = 0.0
    p_gui.params.v_max = 1.0

    functions_graph = FunctionsGraph.from_function_composition([random_binomial_gui])

    fiat_run(functions_graph)


if __name__ == "__main__":
    with_gui()
    # manual_debug()
