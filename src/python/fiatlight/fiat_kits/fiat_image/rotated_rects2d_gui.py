"""GUI registration for `RotatedRects2D` — text-only summary."""

from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .rotated_rects2d_types import RotatedRects2D


def _present(rects: RotatedRects2D) -> None:
    n = int(rects.shape[0]) if rects.ndim >= 1 else 0
    if n == 0:
        imgui.text("0 rotated rects")
        return
    imgui.text(f"{n} rotated rect(s) / ellipse(s)")
    if imgui.tree_node("First 10"):
        for i in range(min(10, n)):
            cx, cy, w, h, ang = (float(v) for v in rects[i])
            imgui.text(f"#{i}: c=({cx:.1f}, {cy:.1f}) {w:.1f}x{h:.1f} {ang:+.1f}°")
        imgui.tree_pop()


def _present_str(rects: RotatedRects2D) -> str:
    n = int(rects.shape[0]) if rects.ndim >= 1 else 0
    return f"RotatedRects2D[n={n}]"


def _register() -> None:
    import numpy as np

    register_callbacks(
        RotatedRects2D,
        present=_present,
        present_str=_present_str,
        default=lambda: RotatedRects2D(np.empty((0, 5), dtype=np.float32)),
    )
