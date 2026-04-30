"""GUI registrations for the `Contours` and `ContoursHierarchy` types.

Text-only summaries; visualization on top of an image is the job of a
`drawContours` node. We use `register_callbacks` so the per-type
boilerplate stays minimal — see _plans/anydatawithgui_ergonomics__spec.md.
"""

from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .contours_types import Contours, ContoursHierarchy


def _present_contours(contours: Contours) -> None:
    n = len(contours)
    total_points = sum(int(c.shape[0]) for c in contours)
    imgui.text(f"{n} contour(s), {total_points} total point(s)")
    if n == 0:
        return
    if imgui.tree_node("Per-contour point counts"):
        for i, c in enumerate(contours):
            imgui.text(f"#{i}: {int(c.shape[0])} points")
        imgui.tree_pop()


def _present_str_contours(contours: Contours) -> str:
    n = len(contours)
    total_points = sum(int(c.shape[0]) for c in contours)
    return f"Contours[n={n}, points={total_points}]"


def _present_hierarchy(hierarchy: ContoursHierarchy) -> None:
    if hierarchy is None or hierarchy.size == 0:
        imgui.text("hierarchy: empty")
        return
    n = int(hierarchy.shape[1]) if hierarchy.ndim == 3 else int(hierarchy.shape[0])
    roots = int((hierarchy[0, :, 3] == -1).sum()) if hierarchy.ndim == 3 else 0
    imgui.text(f"{n} entries, {roots} root contour(s)")


def _present_str_hierarchy(hierarchy: ContoursHierarchy) -> str:
    if hierarchy is None or hierarchy.size == 0:
        return "ContoursHierarchy[empty]"
    n = int(hierarchy.shape[1]) if hierarchy.ndim == 3 else int(hierarchy.shape[0])
    return f"ContoursHierarchy[n={n}]"


def _register() -> None:
    register_callbacks(
        Contours,
        present=_present_contours,
        present_str=_present_str_contours,
        default=lambda: Contours([]),
    )
    register_callbacks(
        ContoursHierarchy,
        present=_present_hierarchy,
        present_str=_present_str_hierarchy,
    )
