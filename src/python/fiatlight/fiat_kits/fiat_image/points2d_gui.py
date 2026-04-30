"""GUI for the `Points2D` type — text-only summary."""

from imgui_bundle import imgui

from fiatlight.fiat_core import AnyDataWithGui
from .points2d_types import Points2D


class Points2DWithGui(AnyDataWithGui[Points2D]):
    """Read-only summary GUI for an (N, 2) array of 2D points."""

    def __init__(self) -> None:
        super().__init__(Points2D)
        self.callbacks.present = self._present
        self.callbacks.present_str = self._present_str
        self.callbacks.default_value_provider = self._default
        self.callbacks.present_collapsible = True

    @staticmethod
    def _default() -> Points2D:
        import numpy as np

        return Points2D(np.empty((0, 2), dtype=np.int32))

    @staticmethod
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

    @staticmethod
    def _present_str(points: Points2D) -> str:
        n = int(points.shape[0]) if points.ndim >= 1 else 0
        return f"Points2D[n={n}]"
