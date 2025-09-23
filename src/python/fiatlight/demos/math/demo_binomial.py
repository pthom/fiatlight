from imgui_bundle import implot, hello_imgui, imgui_knobs

import numpy as np
from typing import Tuple
from numpy.typing import NDArray


def random_binomial(n: int = 50, p: float = 0.1) -> NDArray[np.int32]:
    """
    Make a binomial distribution.

    :param n: Number of trials.
    :param p: Probability of success.
    :return: The binomial distribution.
    """
    r = np.random.binomial(n, p, size=10000)
    return r


def present_histogram(values: NDArray[np.int32]) -> None:
    if implot.begin_plot("Binomial distribution", hello_imgui.em_to_vec2(40, 25)):
        implot.plot_histogram("Binomial", values, bins=50)
        implot.end_plot()


def edit_probability(p: float) -> Tuple[bool, float]:
    changed, p = imgui_knobs.knob("Probability", p, 0.0, 1.0)
    return changed, p


def edit_n(n: int) -> Tuple[bool, int]:
    changed, n = imgui_knobs.knob_int("Number of trials", n, 1, 100)
    return changed, n


def main() -> None:
    import fiatlight as fl

    random_binomial_gui = fl.FunctionWithGui(random_binomial)
    random_binomial_gui.output().set_present_callback(present_histogram)

    random_binomial_gui.input("p").set_edit_callback(edit_probability, edit_collapsible=True)
    random_binomial_gui.input("n").set_edit_callback(edit_n, edit_collapsible=True)

    fl.run(random_binomial_gui)


if __name__ == "__main__":
    main()
