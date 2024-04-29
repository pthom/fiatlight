"""A simple example of plotting a curve using fiatlight

We use FloatMatrix_Dim2 (which is an alias for np.ndarray[ShapeDim2, AnyFloat]) to represent a 2D array of floats.
We instruct fiatlight to display 2D arrays as plots, by calling present_float2_arrays_as_plot().
"""
from fiatlight.fiat_array import FloatMatrix_Dim2
from fiatlight.fiat_types import Float_0_100
import fiatlight


def make_spirograph_curve(
    radius_fixed_circle: Float_0_100 = Float_0_100(10.84),
    radius_moving_circle: Float_0_100 = Float_0_100(3.48),
    pen_offset: Float_0_100 = Float_0_100(6.0),
    nb_turns: Float_0_100 = Float_0_100(23.0),
) -> FloatMatrix_Dim2:
    """a spirograph-like curve"""
    import numpy as np

    t = np.linspace(0, 2 * np.pi * nb_turns, int(500 * nb_turns))
    x = (radius_fixed_circle + radius_moving_circle) * np.cos(t) - pen_offset * np.cos(
        (radius_fixed_circle + radius_moving_circle) / radius_moving_circle * t
    )
    y = (radius_fixed_circle + radius_moving_circle) * np.sin(t) - pen_offset * np.sin(
        (radius_fixed_circle + radius_moving_circle) / radius_moving_circle * t
    )
    return np.array([x, y])  # type: ignore


def main() -> None:
    fiatlight.fiat_array.present_float2_arrays_as_plot()  # instruct fiatlight to display 2D arrays as plots
    fiatlight.fiat_run(make_spirograph_curve)


if __name__ == "__main__":
    main()
