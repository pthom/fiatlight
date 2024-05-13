import fiatlight
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def interactive_sine_wave(freq: float = 1.0, phase: float = 0.0, amplitude: float = 1.0) -> Figure:
    """Generate an interactive sine wave with adjustable frequency, phase, and amplitude."""
    x = np.linspace(0, 2 * np.pi, 3000)
    y = amplitude * np.sin(2 * np.pi * freq * x + phase)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_ylim([-1.5, 1.5])  # Adjust the y-axis limits
    return fig


interactive_sine_wave.freq__range = (0.1, 10)  # type: ignore
interactive_sine_wave.phase__range = (-np.pi, np.pi)  # type: ignore
interactive_sine_wave.amplitude__range = (0.1, 2)  # type: ignore

# And we run the function with the GUI
fiatlight.fiat_run(interactive_sine_wave)
