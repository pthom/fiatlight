"""A simple example of plotting a curve using fiatlight

We use FloatMatrix_Dim2 (which is an alias for np.ndarray[ShapeDim2, AnyFloat]) to represent a 2D array of floats.
It will be presented as a plot with ImPlot / SimplePlotGui in the GUI.
"""

from fiatlight.fiat_kits.fiat_implot import FloatMatrix_Dim2
import fiatlight as fl


@fl.with_fiat_attributes(
    radius_fixed_circle__range=(0.0, 100.0),
    radius_moving_circle__range=(0.0, 100.0),
    pen_offset__range=(0.0, 100.0),
    nb_turns__range=(0.0, 100.0),
)
def make_spirograph_curve(
    radius_fixed_circle: float = 10.84,
    radius_moving_circle: float = 3.48,
    pen_offset: float = 6.0,
    nb_turns: float = 23.0,
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
    fl.run(make_spirograph_curve)


if __name__ == "__main__":
    main()
