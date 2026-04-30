"""GUI for the `Contours` type — text-only summary.

Visualisation of contours over an image is the job of a `draw_contours`
node. The summary here only conveys the structural facts (how many
contours, how many points), so users can sanity-check the output of a
`find_contours` node without wiring a renderer.
"""

from imgui_bundle import imgui

from fiatlight.fiat_core import AnyDataWithGui
from .contours_types import Contours


class ContoursWithGui(AnyDataWithGui[Contours]):
    """Read-only summary GUI for a list of OpenCV contours."""

    def __init__(self) -> None:
        super().__init__(Contours)
        self.callbacks.present = self._present
        self.callbacks.present_str = self._present_str
        self.callbacks.default_value_provider = lambda: Contours([])
        self.callbacks.present_collapsible = True

    @staticmethod
    def _present(contours: Contours) -> None:
        n = len(contours)
        total_points = sum(int(c.shape[0]) for c in contours)
        imgui.text(f"{n} contour(s), {total_points} total point(s)")
        if n == 0:
            return
        if imgui.tree_node("Per-contour point counts"):
            for i, c in enumerate(contours):
                imgui.text(f"#{i}: {int(c.shape[0])} points")
            imgui.tree_pop()

    @staticmethod
    def _present_str(contours: Contours) -> str:
        n = len(contours)
        total_points = sum(int(c.shape[0]) for c in contours)
        return f"Contours[n={n}, points={total_points}]"
