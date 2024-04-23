import numpy as np
from fiatlight.fiat_array.array_types import FloatMatrix_Dim1
from fiatlight import fiat_run


def foo() -> FloatMatrix_Dim1:
    x = np.arange(0, 10, 0.5)
    y = np.sin(x)
    return y  # type: ignore
    # return np.array([1, 2, 3, 4, 5], np.float32)  # type: ignore


def main() -> None:
    from fiatlight.fiat_core import to_function_with_gui
    from fiatlight.fiat_array.simple_plot_gui import SimplePlotGui

    foo_gui = to_function_with_gui(foo)
    foo_gui._outputs_with_gui[0].data_with_gui = SimplePlotGui()
    fiat_run(foo_gui)


if __name__ == "__main__":
    main()
