import math
import numpy as np
from fiatlight.fiat_array import FloatMatrix_Dim1
from fiatlight.fiat_types import Float_0_1, Float_0_100
import fiatlight


def make_range(start: Float_0_100 = 0, stop: Float_0_100 = math.pi * 4, step: Float_0_1 = 0.01) -> FloatMatrix_Dim1:
    return np.arange(start, stop, step)  # type: ignore


def make_sin(x: FloatMatrix_Dim1) -> FloatMatrix_Dim1:
    return np.sin(x)


def main() -> None:
    fiatlight.fiat_array.present_float1_arrays_as_plot()
    fiatlight.fiat_run_composition([make_range, make_sin])


if __name__ == "__main__":
    main()
