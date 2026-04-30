"""GUI registration for the `Circles2D` type — text-only summary."""

from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .circles2d_types import Circles2D


def _present(circles: Circles2D) -> None:
    n = int(circles.shape[0]) if circles.ndim >= 1 else 0
    if n == 0:
        imgui.text("0 circles")
        return
    r_min, r_max = int(circles[:, 2].min()), int(circles[:, 2].max())
    imgui.text(f"{n} circle(s), radius=[{r_min},{r_max}]")
    if imgui.tree_node("First 10"):
        for i in range(min(10, n)):
            cx, cy, r = (int(v) for v in circles[i])
            imgui.text(f"#{i}: center=({cx}, {cy}) r={r}")
        imgui.tree_pop()


def _present_str(circles: Circles2D) -> str:
    n = int(circles.shape[0]) if circles.ndim >= 1 else 0
    return f"Circles2D[n={n}]"


def _register() -> None:
    import numpy as np

    register_callbacks(
        Circles2D,
        present=_present,
        present_str=_present_str,
        default=lambda: Circles2D(np.empty((0, 3), dtype=np.int32)),
    )
