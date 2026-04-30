"""GUI registration for the `Lines2D` type — text-only summary."""

from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .lines2d_types import Lines2D


def _present(lines: Lines2D) -> None:
    n = int(lines.shape[0]) if lines.ndim >= 1 else 0
    if n == 0:
        imgui.text("0 lines")
        return
    x_min = int(min(lines[:, 0].min(), lines[:, 2].min()))
    y_min = int(min(lines[:, 1].min(), lines[:, 3].min()))
    x_max = int(max(lines[:, 0].max(), lines[:, 2].max()))
    y_max = int(max(lines[:, 1].max(), lines[:, 3].max()))
    imgui.text(f"{n} line(s), bbox x=[{x_min},{x_max}] y=[{y_min},{y_max}]")
    if imgui.tree_node("First 10"):
        for i in range(min(10, n)):
            x1, y1, x2, y2 = (int(v) for v in lines[i])
            imgui.text(f"#{i}: ({x1}, {y1}) -> ({x2}, {y2})")
        imgui.tree_pop()


def _present_str(lines: Lines2D) -> str:
    n = int(lines.shape[0]) if lines.ndim >= 1 else 0
    return f"Lines2D[n={n}]"


def _register() -> None:
    import numpy as np

    register_callbacks(
        Lines2D,
        present=_present,
        present_str=_present_str,
        default=lambda: Lines2D(np.empty((0, 4), dtype=np.int32)),
    )
