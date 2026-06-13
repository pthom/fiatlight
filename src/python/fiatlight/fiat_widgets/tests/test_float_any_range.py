"""Range-inference / state logic for the any-range float slider (no imgui)."""
import pytest

from fiatlight.fiat_widgets.float_widgets import (
    AnyRangeSliderState,
    _infer_range_max,
    _update_range_state,
)


def test_infer_range_max() -> None:
    assert _infer_range_max(0.0) == 1.0
    assert _infer_range_max(0.3) == pytest.approx(1.0)
    assert _infer_range_max(0.03) == pytest.approx(0.1)
    assert _infer_range_max(5.0) == pytest.approx(10.0)
    assert _infer_range_max(50.0) == pytest.approx(100.0)
    assert _infer_range_max(5e7) == pytest.approx(1e8)


def test_infers_on_first_use() -> None:
    s = AnyRangeSliderState()
    _update_range_state(s, 5.0, accept_negative=True)
    assert s.range_max == pytest.approx(10.0)
    assert s.symmetric is False
    assert s.log is False


def test_symmetric_inferred_for_negative_value() -> None:
    s = AnyRangeSliderState()
    _update_range_state(s, -5.0, accept_negative=True)
    assert s.range_max == pytest.approx(10.0)
    assert s.symmetric is True


def test_no_negative_forces_positive_range() -> None:
    s = AnyRangeSliderState()
    _update_range_state(s, -5.0, accept_negative=False)
    assert s.symmetric is False


def test_log_auto_on_for_wide_range() -> None:
    s = AnyRangeSliderState()
    _update_range_state(s, 5e7, accept_negative=True)
    assert s.range_max == pytest.approx(1e8)
    assert s.log is True


def test_range_grows_but_never_shrinks() -> None:
    s = AnyRangeSliderState(range_max=100.0)
    _update_range_state(s, 5.0, accept_negative=True)  # 5 fits within 100
    assert s.range_max == pytest.approx(100.0)  # not shrunk
    _update_range_state(s, 5000.0, accept_negative=True)  # needs 10_000
    assert s.range_max == pytest.approx(10000.0)  # grown
