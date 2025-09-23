import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def lissajous_curve(
    freq1: float = 5.0, freq2: float = 4.0, delta: float = np.pi / 2, nb_periods: float = 1
) -> plt.Figure:  # type: ignore
    """Creates a Lissajous curve, and returns a Matplotlib figure."""
    t = np.linspace(0, 2 * np.pi * nb_periods, 10_000)
    x = np.sin(freq1 * t + delta)
    y = np.sin(freq2 * t)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    return fig


# Add a GUI to the code in a few seconds, using fiatlight
import fiatlight as fl

# Optional: set the range of the parameters
fl.add_fiat_attributes(
    lissajous_curve,
    freq1__range=(0, 10),
    freq2__range=(0, 10),
    delta__range=(-np.pi, np.pi),
    nb_periods__range=(0.1, 10),
)

# Run the function interactively
fl.run(lissajous_curve, app_name="Interactive Lissajou Curve")
