from imgui_bundle import imgui, ImVec4, imgui_ctx, hello_imgui
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import fontawesome_6_ctx
from typing import Dict, Tuple, NewType
from enum import Enum
import time
import math
import copy


class _ButtonRangeAction(Enum):
    NONE = 1
    MULTIPLY = 2
    DIVIDE = 3


# Buttons to change the range
def _show_buttons_range(tooltip_mul, tooltip_div) -> _ButtonRangeAction:
    from fiatlight.fiat_widgets.draw_symbols import draw_symbol, SymbolDrawing

    r = _ButtonRangeAction.NONE
    from fiatlight.fiat_widgets import fiat_osd

    orig_cursor_pos = imgui.get_cursor_pos()
    cur_pos = copy.copy(orig_cursor_pos)

    btn_size = hello_imgui.em_to_vec2(0.7, 0.65)
    if imgui.button("##x", btn_size):
        r = _ButtonRangeAction.MULTIPLY
    draw_symbol(cur_pos, btn_size, SymbolDrawing.ArrowUp)
    fiat_osd.set_widget_tooltip(tooltip_mul)
    cur_pos.y += hello_imgui.em_size(0.7)
    imgui.set_cursor_pos(cur_pos)
    if imgui.button("##10-", btn_size):
        r = _ButtonRangeAction.DIVIDE
    draw_symbol(cur_pos, btn_size, SymbolDrawing.ArrowDown)
    fiat_osd.set_widget_tooltip(tooltip_div)

    final_cursor_pos = orig_cursor_pos
    final_cursor_pos.x += hello_imgui.em_size(0.8)
    imgui.set_cursor_pos(final_cursor_pos)

    return r


def _show_zero_button() -> bool:
    from fiatlight.fiat_widgets.draw_symbols import draw_symbol, SymbolDrawing

    clicked = False
    from fiatlight.fiat_widgets import fiat_osd

    orig_cursor_pos = imgui.get_cursor_pos()
    btn_pos = copy.copy(orig_cursor_pos)
    btn_pos.y += hello_imgui.em_size(0.3)
    imgui.set_cursor_pos(btn_pos)
    btn_size = hello_imgui.em_to_vec2(0.7, 0.65)
    if imgui.button("##0", btn_size):
        clicked = True
    draw_symbol(btn_pos, btn_size, SymbolDrawing.Zero)
    fiat_osd.set_widget_tooltip("Set to zero")

    final_cursor_pos = orig_cursor_pos
    final_cursor_pos.x += hello_imgui.em_size(0.8)
    imgui.set_cursor_pos(final_cursor_pos)

    return clicked


#######################################################################################################################
# slider_any_positive_float(label: str, v: float, nb_significant_digits: int = 4) -> Tuple[bool, float]:
#     """A slider that can edit *positive* floats, with a given number of significant digits
#     for any value (the slider will interactively adapt its range to the value,
#     and flash red when the range changed)
#     """
#######################################################################################################################
class _SliderFloatAdaptiveInterval:
    nb_significant_digits: int = 4
    current_power: int = 1
    time_last_power_change: float = 0.0

    def __init__(self, nb_significant_digits: int = 4) -> None:
        self.nb_significant_digits = nb_significant_digits

    def interval_max(self) -> float:
        return math.pow(10, self.current_power)

    def set_target_value(self, target_value: float) -> None:
        assert target_value >= 0.0

        if target_value == 0.0:
            if self.current_power != 1:
                self.time_last_power_change = time.time()
            self.current_power = 1
            return

        k = 0.1
        trigger_max = self.interval_max() * (1 - k)
        if target_value > trigger_max:
            self.time_last_power_change = time.time()
            self.current_power += 1
            return

        trigger_min = self.interval_max() * k * 0.9
        if target_value < trigger_min:
            self.time_last_power_change = time.time()
            self.current_power -= 1
            return

    def format_string(self) -> str:
        float_format = f"%.{self.nb_significant_digits}g"
        max_value_formatted = float_format % self.interval_max()
        r = f"{float_format}  (0 - {max_value_formatted})"
        return r

    def was_changed_recently(self) -> bool:
        if self.time_last_power_change == 0.0:
            return False
        return (time.time() - self.time_last_power_change) < 0.5


class _SliderFloatAdaptiveIntervalCache:
    intervals: Dict[int, _SliderFloatAdaptiveInterval]

    def __init__(self) -> None:
        self.intervals = {}

    def get_or_create(self, id: int, nb_significant_digits: int) -> _SliderFloatAdaptiveInterval:
        if id not in self.intervals:
            self.intervals[id] = _SliderFloatAdaptiveInterval(nb_significant_digits)
        return self.intervals[id]


_SLIDER_FLOAT_ADAPTIVE_INTERVAL_CACHE = _SliderFloatAdaptiveIntervalCache()


def slider_any_positive_float(label: str, v: float, nb_significant_digits: int = 4) -> Tuple[bool, float]:
    """A slider that can edit *positive* floats, with a given number of significant digits
    for any value (the slider will interactively adapt its range to the value,
    and flash red when the range changed)
    """

    global _SLIDER_FLOAT_ADAPTIVE_INTERVAL_CACHE
    float32_max = 3.4028234663852886e38
    max_value = float32_max / 10
    if v > max_value:
        v = max_value
        return True, v

    label_id = imgui.get_id(label)
    interval = _SLIDER_FLOAT_ADAPTIVE_INTERVAL_CACHE.get_or_create(label_id, nb_significant_digits)

    with imgui_ctx.begin_horizontal(label):
        with imgui_ctx.push_id(str(interval.current_power)):
            changed_via_button = False
            new_value = v

            # Display the buttons to change the range
            action = _show_buttons_range("Multiply by 10", "Divide by 10")
            if action == _ButtonRangeAction.MULTIPLY:
                changed_via_button = True
                new_value *= 10
            elif action == _ButtonRangeAction.DIVIDE:
                changed_via_button = True
                new_value /= 10

            if _show_zero_button():
                new_value = 0.0
                changed_via_button = True

            # Display the slider
            was_changed_recently = interval.was_changed_recently()
            if was_changed_recently:
                imgui.push_style_color(imgui.Col_.frame_bg_hovered.value, ImVec4(1, 0, 0, 1))
            changed_slider, new_value = imgui.slider_float(
                label, new_value, 0.0, interval.interval_max(), interval.format_string()
            )
            if was_changed_recently:
                imgui.pop_style_color()
            interval.set_target_value(new_value)

    changed = changed_slider or changed_via_button
    return changed, new_value


#######################################################################################################################
# slider_any_float_log_scale(label: str, v: float) -> Tuple[bool, float]:
#     """A slider that can edit floats, with a logarithmic scale
#     (the range can be adapted by the user)
#     """
#######################################################################################################################
PowerOfTen = NewType("PowerOfTen", int)


class _PowerOfTenCache:
    power_of_ten: Dict[int, PowerOfTen]

    def __init__(self) -> None:
        self.power_of_ten = {}

    def _compute_power_of_ten(self, current_float_value: float) -> PowerOfTen:
        if current_float_value == 0.0:
            return 1
        abs_value = abs(current_float_value)
        return PowerOfTen(int(math.ceil(math.log10(abs_value))))

    def get_or_create(self, id: int, current_float_value: float) -> PowerOfTen:
        if id not in self.power_of_ten:
            self.power_of_ten[id] = self._compute_power_of_ten(current_float_value)
        return self.power_of_ten[id]


_POWER_OF_TEN_CACHE = _PowerOfTenCache()


def slider_any_float_log_scale(
    label: str, v: float, accept_negative: bool = True, nb_displayed_digit=4
) -> Tuple[bool, float]:
    with fontawesome_6_ctx():
        with imgui_ctx.begin_horizontal("slider_any_float_log_scale" + label):
            power_of_ten = _POWER_OF_TEN_CACHE.get_or_create(imgui.get_id(label), v)
            max_value = math.pow(10, power_of_ten)
            if accept_negative:
                min_value = -max_value
            else:
                min_value = 0.0

            # Display the buttons to change the range
            tooltip_range = f"\n(current range: [{min_value}, {max_value}])"
            action = _show_buttons_range("Multiply range by 10" + tooltip_range, "Divide range by 10" + tooltip_range)
            if action == _ButtonRangeAction.MULTIPLY:
                power_of_ten += 1
                _POWER_OF_TEN_CACHE.power_of_ten[imgui.get_id(label)] = power_of_ten
            elif action == _ButtonRangeAction.DIVIDE:
                power_of_ten -= 1
                _POWER_OF_TEN_CACHE.power_of_ten[imgui.get_id(label)] = power_of_ten

            # Work around a bug in imgui: we need to display more digits for small values
            if v != 0:
                v_log = math.log10(math.fabs(v))
                nb_min_displayed_digit = -int(v_log) + 1
                if nb_displayed_digit < nb_min_displayed_digit:
                    nb_displayed_digit = nb_min_displayed_digit

            # Display the logarithmic slider
            format_string = f"%.{nb_displayed_digit}g"
            changed, new_value = imgui.slider_float(
                label, v, min_value, max_value, format_string, imgui.SliderFlags_.logarithmic.value
            )

    return changed, new_value


def sandbox() -> None:
    from imgui_bundle import hello_imgui

    value1 = 300.0
    value2 = 3.0

    value_log = 11.0
    value_log_positive = 1.0

    def gui() -> None:
        nonlocal value1, value2, value_log, value_log_positive
        changed, value1 = slider_any_positive_float("##slider", value1)
        changed, value2 = slider_any_positive_float("##slider2", value2)
        changed, value_log = slider_any_float_log_scale("slider_log", value_log)
        changed, value_log_positive = slider_any_float_log_scale(
            "slider_log_pos", value_log_positive, accept_negative=False
        )

    hello_imgui.run(gui)


if __name__ == "__main__":
    sandbox()
