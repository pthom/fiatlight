"""GUI registration for `LabelImage` — colorized via cv2.applyColorMap."""

import cv2
import numpy as np
from imgui_bundle import imgui, immvision

from fiatlight.fiat_togui.simple_gui import register_callbacks

from .label_image_types import LabelImage


_VIEWER_CACHE: dict[int, immvision.ImageParams] = {}


def _colorize(labels: LabelImage) -> np.ndarray:
    if labels.size == 0:
        return np.zeros((1, 1, 3), dtype=np.uint8)
    n = int(labels.max())
    if n == 0:
        return np.zeros((labels.shape[0], labels.shape[1], 3), dtype=np.uint8)
    # Map labels to [0, 255] cycling so adjacent IDs get distinct colors.
    u8 = ((labels.astype(np.int64) * 79) % 256).astype(np.uint8)
    color = cv2.applyColorMap(u8, cv2.COLORMAP_JET)
    color[labels == 0] = (0, 0, 0)
    return color


def _present(labels: LabelImage) -> None:
    n = int(labels.max()) if labels.size else 0
    imgui.text(f"{n} component(s), shape={tuple(labels.shape)}")
    color = _colorize(labels)
    key = id(labels)
    params = _VIEWER_CACHE.get(key)
    if params is None:
        params = immvision.ImageParams()
        params.image_display_size = (300, 0)
        params.show_options_button = False
        _VIEWER_CACHE[key] = params
    immvision.image("##labels", color, params)


def _present_str(labels: LabelImage) -> str:
    n = int(labels.max()) if labels.size else 0
    return f"LabelImage[{tuple(labels.shape)}, n={n}]"


def _register() -> None:
    register_callbacks(
        LabelImage,
        present=_present,
        present_str=_present_str,
        default=lambda: LabelImage(np.zeros((1, 1), dtype=np.int32)),
    )
