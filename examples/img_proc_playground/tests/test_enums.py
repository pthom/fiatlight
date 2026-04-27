"""Sanity checks for the playground's shared enums.

Only non-trivial assertions live here. We do NOT assert
`MyEnum.X.value == cv2.X` — that's tautological because the enum member is
defined as `X = cv2.X` and both sides bind to the same constant at import.
"""
from examples.img_proc_playground.fiat_cv_enums import (
    CannyApertureSize,
    GaussianKsize,
)


def test_canny_aperture_literals() -> None:
    """`cv2.Canny` only accepts apertureSize=3/5/7. We hard-code these values
    rather than mirroring a cv2 constant, so they're worth pinning."""
    assert CannyApertureSize.APERTURE_3.value == 3
    assert CannyApertureSize.APERTURE_5.value == 5
    assert CannyApertureSize.APERTURE_7.value == 7


def test_gaussian_ksize_parity() -> None:
    """Convention: every member must be odd and >= 3."""
    for member in GaussianKsize:
        assert member.value % 2 == 1, f"{member.name} must be odd"
        assert member.value >= 3
