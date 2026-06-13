"""imread_rgb falls back to Pillow when opencv is not installed."""
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("PIL")  # the tests build images with Pillow

from PIL import Image  # noqa: E402
from fiatlight.fiat_kits.fiat_image.imread_rgb import imread_rgb, _imread_rgb_pillow  # noqa: E402


def _save(tmp_path: Path, arr: np.ndarray, mode: str | None = None) -> str:
    p = tmp_path / "img.png"
    Image.fromarray(arr, mode).save(p)
    return str(p)


def test_pillow_reads_rgb(tmp_path: Path) -> None:
    path = _save(tmp_path, np.full((6, 8, 3), 100, np.uint8))
    assert _imread_rgb_pillow(path).shape == (6, 8, 3)


def test_pillow_preserves_alpha(tmp_path: Path) -> None:
    path = _save(tmp_path, np.full((4, 5, 4), 60, np.uint8))
    assert _imread_rgb_pillow(path).shape == (4, 5, 4)


def test_pillow_promotes_gray_to_rgb(tmp_path: Path) -> None:
    path = _save(tmp_path, np.full((4, 4), 30, np.uint8), "L")
    assert _imread_rgb_pillow(path).shape == (4, 4, 3)


def test_imread_rgb_falls_back_without_cv2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Make `import cv2` raise ImportError, forcing the Pillow path.
    monkeypatch.setitem(sys.modules, "cv2", None)
    path = _save(tmp_path, np.full((6, 8, 3), 100, np.uint8))
    assert imread_rgb(path).shape == (6, 8, 3)
