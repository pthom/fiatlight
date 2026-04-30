"""GUI registration for `BlobStats` — text-only summary."""

from imgui_bundle import imgui

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .blob_stats_types import BlobStats


def _present(stats: BlobStats) -> None:
    n = int(stats.shape[0]) if stats.ndim >= 1 else 0
    if n == 0:
        imgui.text("0 blobs")
        return
    # Row 0 is the background blob; the "real" components are rows 1..N-1.
    imgui.text(f"{n} entry(ies) (row 0 = background)")
    if imgui.tree_node("Per-blob (x, y, w, h, area)"):
        for i in range(min(20, n)):
            x, y, w, h, area = (int(v) for v in stats[i])
            tag = " [bg]" if i == 0 else ""
            imgui.text(f"#{i}{tag}: ({x}, {y}) {w}x{h} area={area}")
        if n > 20:
            imgui.text(f"… {n - 20} more")
        imgui.tree_pop()


def _present_str(stats: BlobStats) -> str:
    n = int(stats.shape[0]) if stats.ndim >= 1 else 0
    return f"BlobStats[n={n}]"


def _register() -> None:
    import numpy as np

    register_callbacks(
        BlobStats,
        present=_present,
        present_str=_present_str,
        default=lambda: BlobStats(np.empty((0, 5), dtype=np.int32)),
    )
