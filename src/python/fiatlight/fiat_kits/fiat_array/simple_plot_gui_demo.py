import fiatlight
from fiatlight import fiat_array
from fiatlight.fiat_types import Float_0_100
import numpy as np
import math
import time

_start_time = time.time()


def time_seconds() -> float:
    return time.time() - _start_time


def phase_from_time_seconds(time_: float) -> float:
    return time_ * 15.0


time_seconds.invoke_always_dirty = True  # type: ignore


def sin_wave(phase: float, amplitude: float = 1.0) -> fiat_array.FloatMatrix_Dim2:
    x = np.arange(0, 10, 0.1)
    y = np.sin(x + phase) * amplitude
    r = np.stack((x, y))
    return r  # type: ignore


def make_spirograph_curve(
    radius_fixed_circle: Float_0_100 = Float_0_100(10.84),
    radius_moving_circle: Float_0_100 = Float_0_100(3.48),
    pen_offset: Float_0_100 = Float_0_100(6.0),
    nb_turns: Float_0_100 = Float_0_100(23.0),
) -> fiat_array.FloatMatrix_Dim2:
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


def get_simple_values(x: float) -> fiat_array.FloatMatrix_Dim1:
    r = []
    for i in range(10):
        r.append(math.cos(x**i))
    return np.array(r)  # type: ignore


def sandbox() -> None:
    graph = fiatlight.FunctionsGraph()
    graph.add_function(make_spirograph_curve)
    graph.add_function(get_simple_values)

    graph.add_function(time_seconds)
    graph.add_function(phase_from_time_seconds)
    graph.add_function(sin_wave)
    graph.add_link("time_seconds", "phase_from_time_seconds")
    graph.add_link("phase_from_time_seconds", "sin_wave")

    fiatlight.fiat_run_graph(graph)


if __name__ == "__main__":
    sandbox()
