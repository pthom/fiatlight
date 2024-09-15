# Part 1: Standard Python code (without GUI)
# ------------------------------------------
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import fiatlight as fl


def lissajous_curve(freq1: float = 5.0, freq2: float = 4.0, delta: float = np.pi / 2, nb_periods: float = 1) -> Figure:
    """Creates a Lissajous curve, and returns a Matplotlib figure."""
    t = np.linspace(0, 2 * np.pi * nb_periods, 10_000)
    x = np.sin(freq1 * t + delta)
    y = np.sin(freq2 * t)
    fig = plt.figure(figsize=(5, 5))
    plt.plot(x, y)
    return fig


# Part 2: Add a GUI to the code in a few seconds
# ----------------------------------------------

# Options for widgets
fl.add_fiat_attributes(
    lissajous_curve,
    freq1__range=(0, 10),
    freq2__range=(0, 10),
    delta__range=(-np.pi, np.pi),
    nb_periods__range=(0.1, 10),
    nb_periods__edit_type="knob",
)

# Run the function interactively
fl.run(lissajous_curve, app_name="Interactive Lissajou Curve")
