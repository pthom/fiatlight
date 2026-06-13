import pytest

pytest.importorskip("cv2")  # cv_color_type imports cv2; skip when opencv is not installed.

from fiatlight.fiat_kits.fiat_image import cv_color_type  # noqa: E402


def test_truc() -> None:
    color = cv_color_type.ColorType.BGR
    outputs = color.available_conversion_outputs()
    print(outputs)
