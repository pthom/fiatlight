"""slider_float_any_range: edit a float of any magnitude with a slider whose
range the user controls.

The range (a power of ten) is inferred from the current value, then adjustable
with ÷10 / x10. `±` toggles a symmetric range [-max, max] so negatives can be
slid through zero; `log` switches to a logarithmic scale. Ctrl/double-click the
slider to type an exact value. The state is transient (re-inferred from the
value on reload — the value itself is what persists)."""

from imgui_bundle import imgui, imgui_ctx, hello_imgui
from fiatlight.fiat_widgets import mini_buttons
from dataclasses import dataclass
from typing import Tuple
import math


# Range bounds and the magnitude at/above which we default to a log scale.
_RANGE_MAX_CEIL = 1e12
_RANGE_MAX_FLOOR = 1e-9
_LOG_AUTO_THRESHOLD = 1000.0


def _str_until_double_hash(s: str) -> str:
    """Return the string until the first double hash `##`"""
    idx = s.find("##")
    if idx == -1:
        return s
    return s[:idx]


def _get_next_item_width() -> float:
    g = imgui.get_current_context()
    if not g.next_item_data.has_flags & imgui.internal.NextItemDataFlags_.has_width.value:
        return -1.0
    return g.next_item_data.width


def _get_slider_width() -> float:
    next_item_width = _get_next_item_width()
    if next_item_width > 0.0:
        return next_item_width
    return hello_imgui.em_size(10)


@dataclass
class AnyRangeSliderState:
    """Transient per-instance state for `slider_float_any_range`. Inferred from
    the value on first use; the ÷10 / x10 / log / ± controls override it during a
    session. Not persisted — re-inferred from the (persisted) value on reload."""

    range_max: float | None = None  # a power of ten; None until inferred
    symmetric: bool = False  # range is [-range_max, range_max] when True
    log: bool = False
    # Double-click swaps the slider for a (focus-grabbing, unclamped) text input.
    editing: bool = False
    focus_input: bool = False


def _infer_range_max(value_abs: float) -> float:
    """Smallest power of ten >= |value| (1.0 for value 0)."""
    if value_abs <= 0.0:
        return 1.0
    return float(10.0 ** math.ceil(math.log10(value_abs)))


def _update_range_state(state: AnyRangeSliderState, value: float, accept_negative: bool) -> None:
    """Initialize the range from the value on first use, and grow it (never
    shrink here) if the value no longer fits. Pure logic, no imgui — unit-tested."""
    if not accept_negative:
        state.symmetric = False
    needed_max = _infer_range_max(abs(value))
    if state.range_max is None:
        state.range_max = needed_max
        state.symmetric = accept_negative and value < 0.0
        state.log = (not state.symmetric) and state.range_max >= _LOG_AUTO_THRESHOLD
    elif needed_max > state.range_max:
        state.range_max = needed_max


def _toggle_button(text: str, active: bool, tooltip: str) -> bool:
    """A small button that reads as 'pressed' when `active`."""
    from fiatlight.fiat_widgets import fiat_osd

    style = imgui.get_style()
    if active:
        imgui.push_style_color(imgui.Col_.button.value, style.color_(imgui.Col_.button_active.value))
    clicked = imgui.small_button(text)
    if active:
        imgui.pop_style_color()
    fiat_osd.set_widget_tooltip(tooltip)
    return clicked


def slider_float_any_range(
    label: str,
    value: float,
    state: AnyRangeSliderState,
    accept_negative: bool = True,
) -> Tuple[bool, float]:
    """See module docstring. `state` holds the (transient) range; `accept_negative`
    enables the ± symmetric-range toggle. Returns (value_changed, new_value)."""
    _update_range_state(state, value, accept_negative)
    assert state.range_max is not None  # set by _update_range_state

    changed = False
    new_value = value
    with imgui_ctx.push_id(label):
        with imgui_ctx.begin_horizontal("##any_range"):
            # ÷10 / x10 act on the RANGE (a power of ten), not the value.
            action = mini_buttons.show_buttons_range("Multiply range by 10", "Divide range by 10")
            if action == mini_buttons.ButtonRangeAction.MULTIPLY:
                state.range_max = min(state.range_max * 10.0, _RANGE_MAX_CEIL)
            elif action == mini_buttons.ButtonRangeAction.DIVIDE:
                candidate = state.range_max / 10.0
                # Don't shrink below what the current value needs (or the floor).
                if candidate >= _infer_range_max(abs(value)) and candidate >= _RANGE_MAX_FLOOR:
                    state.range_max = candidate

            range_min = -state.range_max if state.symmetric else 0.0
            imgui.set_next_item_width(_get_slider_width())
            if state.editing:
                # Unclamped text input (double-click). Lets you type a value
                # beyond the current range, which then grows to fit.
                if state.focus_input:
                    imgui.set_keyboard_focus_here()
                    state.focus_input = False
                # input_float (an InputScalar) already commits on Enter / defocus
                # and forbids the EnterReturnsTrue flag, so pass no flags.
                changed_input, new_value = imgui.input_float("##input", new_value, 0.0, 0.0, "%.6g")
                changed = changed or changed_input
                if imgui.is_item_deactivated():
                    state.editing = False
            else:
                flags = imgui.SliderFlags_.logarithmic.value if state.log else 0
                changed_slider, new_value = imgui.slider_float(
                    "##slider", new_value, range_min, state.range_max, "%.4g", flags
                )
                changed = changed or changed_slider
                if imgui.is_item_hovered() and imgui.is_mouse_double_clicked(imgui.MouseButton_.left.value):
                    state.editing = True
                    state.focus_input = True

            readout = f"±{state.range_max:.3g}" if state.symmetric else f"0–{state.range_max:.3g}"
            imgui.text_disabled(readout)

            # log toggle — disabled while symmetric (a log scale can't span zero).
            imgui.begin_disabled(state.symmetric)
            if _toggle_button("log", state.log, "Logarithmic scale"):
                state.log = not state.log
            imgui.end_disabled()

            # ± toggle — switch the range between [0, max] and [-max, max].
            if accept_negative:
                if _toggle_button("±", state.symmetric, "Allow negative values (symmetric range)"):
                    state.symmetric = not state.symmetric
                    if state.symmetric:
                        state.log = False

            lbl = _str_until_double_hash(label)
            if len(lbl) > 0:
                imgui.text(lbl)

    return changed, new_value
