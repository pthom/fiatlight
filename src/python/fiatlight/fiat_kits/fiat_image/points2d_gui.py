"""GUI registration for the `Points2D` type — text-only summary."""

import numpy as np
from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .points2d_types import Points2D


def _present(points: Points2D) -> None:
    n = int(points.shape[0]) if points.ndim >= 1 else 0
    if n == 0:
        imgui.text("0 points")
        return
    x_min, y_min = int(points[:, 0].min()), int(points[:, 1].min())
    x_max, y_max = int(points[:, 0].max()), int(points[:, 1].max())
    imgui.text(f"{n} point(s), bbox x=[{x_min},{x_max}] y=[{y_min},{y_max}]")
    if imgui.tree_node("First 10"):
        for i in range(min(10, n)):
            imgui.text(f"#{i}: ({int(points[i, 0])}, {int(points[i, 1])})")
        imgui.tree_pop()


def _present_str(points: Points2D) -> str:
    n = int(points.shape[0]) if points.ndim >= 1 else 0
    return f"Points2D[n={n}]"


def _register() -> None:
    register_callbacks(
        Points2D,
        present=_present,
        present_str=_present_str,
        default=lambda: Points2D(np.empty((0, 2), dtype=np.int32)),
    )
