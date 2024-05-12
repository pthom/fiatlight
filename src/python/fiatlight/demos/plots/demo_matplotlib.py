import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from enum import Enum


def interactive_sine_wave(freq: float = 1.0, phase: float = 0.0, amplitude: float = 1.0) -> Figure:
    """Generate an interactive sine wave with adjustable frequency, phase, and amplitude."""
    x = np.linspace(0, 2 * np.pi, 3000)
    y = amplitude * np.sin(2 * np.pi * freq * x + phase)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_ylim([-1.5, 1.5])  # Adjust the y-axis limits
    return fig


class ColorMap(Enum):
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"


def gaussian_heatmap(
    mean: float = 0, variance: float = 1, colormap: ColorMap = ColorMap.VIRIDIS, levels: int = 10
) -> Figure:
    """Generate a Gaussian heatmap with adjustable mean, variance, colormap, and number of contour levels."""
    x = y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-((X - mean) ** 2 + (Y - mean) ** 2) / (2 * variance))
    fig, ax = plt.subplots()
    contour = ax.contourf(X, Y, Z, levels, cmap=colormap.value)
    fig.colorbar(contour, ax=ax)
    return fig


def data_smoothing(window_size: int = 5) -> Figure:
    """Demonstrate data smoothing using a moving average filter."""
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(0, 0.1, 100)  # noisy sine wave
    y_smooth = np.convolve(y, np.ones(window_size) / window_size, mode="same")

    fig, ax = plt.subplots()
    ax.plot(x, y, label="Original")
    ax.plot(x, y_smooth, label="Smoothed")
    ax.legend()
    return fig


def interactive_histogram(n_bars: int = 10, mu: float = 0, sigma: float = 1) -> Figure:
    """Generate an interactive histogram with adjustable number of bars, mean, and standard deviation."""
    data = np.random.normal(mu, sigma, 1000)
    bins = np.linspace(np.min(data), np.max(data), n_bars)

    fig, ax = plt.subplots()
    ax.hist(data, bins=bins, color="blue", alpha=0.7)
    return fig


def main() -> None:
    import fiatlight

    graph = fiatlight.FunctionsGraph()
    graph.add_function(interactive_sine_wave)
    graph.add_function(gaussian_heatmap)
    graph.add_function(data_smoothing)
    graph.add_function(interactive_histogram)
    fiatlight.fiat_run_graph(graph)


if __name__ == "__main__":
    main()
