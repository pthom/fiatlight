"""GUI registration for the `Rects2D` type — text-only summary."""

from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .rects2d_types import Rects2D


def _present(rects: Rects2D) -> None:
    n = int(rects.shape[0]) if rects.ndim >= 1 else 0
    if n == 0:
        imgui.text("0 rects")
        return
    w_min, w_max = int(rects[:, 2].min()), int(rects[:, 2].max())
    h_min, h_max = int(rects[:, 3].min()), int(rects[:, 3].max())
    imgui.text(f"{n} rect(s), w=[{w_min},{w_max}] h=[{h_min},{h_max}]")
    if imgui.tree_node("First 10"):
        for i in range(min(10, n)):
            x, y, w, h = (int(v) for v in rects[i])
            imgui.text(f"#{i}: ({x}, {y}) {w}x{h}")
        imgui.tree_pop()


def _present_str(rects: Rects2D) -> str:
    n = int(rects.shape[0]) if rects.ndim >= 1 else 0
    return f"Rects2D[n={n}]"


def _register() -> None:
    import numpy as np

    register_callbacks(
        Rects2D,
        present=_present,
        present_str=_present_str,
        default=lambda: Rects2D(np.empty((0, 4), dtype=np.int32)),
    )
