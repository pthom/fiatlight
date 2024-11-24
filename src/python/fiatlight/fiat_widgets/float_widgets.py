from imgui_bundle import imgui, ImVec4, imgui_ctx, hello_imgui
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import fontawesome_6_ctx
from fiatlight.fiat_widgets import mini_buttons
from typing import Dict, Tuple, NewType
import time
import math


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
        r = next_item_width
    else:
        r = hello_imgui.em_size(10)
    return r


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
        assert nb_significant_digits > 0
        self.nb_significant_digits = nb_significant_digits

    def interval_max(self) -> float:
        return math.pow(10, self.current_power)

    def set_target_value(self, target_value: float) -> None:
        assert target_value >= 0.0

        if target_value == 0.0:
            if self.current_power != 1:
                self.time_last_power_change = time.time()
            self.current_power = 0
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

    def format_string(self, is_positive: bool) -> str:
        float_format = f"%.{self.nb_significant_digits}g"
        max_value_formatted = float_format % self.interval_max()
        if not is_positive:
            max_value_formatted = float_format % (-self.interval_max())
        r = f"{float_format}  (0 ... {max_value_formatted})"
        if not is_positive:
            r = f"-{r}"
        return r

    def was_changed_recently(self) -> bool:
        if self.time_last_power_change == 0.0:
            return False
        return (time.time() - self.time_last_power_change) < 0.5


class _SliderFloatAdaptiveIntervalCache:
    intervals: Dict[int, _SliderFloatAdaptiveInterval]

    def __init__(self) -> None:
        self.intervals = {}

    def get_or_create(self, id_: int, nb_significant_digits: int) -> _SliderFloatAdaptiveInterval:
        if id_ not in self.intervals:
            self.intervals[id_] = _SliderFloatAdaptiveInterval(nb_significant_digits)
        return self.intervals[id_]


_SLIDER_FLOAT_ADAPTIVE_INTERVAL_CACHE = _SliderFloatAdaptiveIntervalCache()


def slider_float_any_range(
    label: str, _v: float, accept_negative: bool = True, nb_significant_digits: int = 4
) -> Tuple[bool, float]:
    """A slider that can edit *positive* floats, with a given number of significant digits
    for any value (the slider will interactively adapt its range to the value,
    and flash red when the range changed)
    """
    slider_width = _get_slider_width()
    imgui.begin_group()
    imgui.push_id(label)

    if not accept_negative and _v < 0:
        raise ValueError("The value must be positive")

    v_abs = abs(_v)
    is_positive = _v >= 0
    sign = 1 if is_positive else -1

    global _SLIDER_FLOAT_ADAPTIVE_INTERVAL_CACHE
    float32_max = 3.4028234663852886e38
    max_value = float32_max / 10
    if v_abs > max_value:
        v_abs = max_value
        return True, v_abs * sign

    label_id = imgui.get_id(label)
    interval = _SLIDER_FLOAT_ADAPTIVE_INTERVAL_CACHE.get_or_create(label_id, nb_significant_digits)

    with imgui_ctx.begin_horizontal(label):
        with imgui_ctx.push_id(str(interval.current_power)):
            changed_via_button = False
            new_value_abs = v_abs

            # Display the buttons to change the range
            action = mini_buttons.show_buttons_range("Multiply by 10", "Divide by 10")
            if action == mini_buttons.ButtonRangeAction.MULTIPLY:
                changed_via_button = True
                new_value_abs *= 10
            elif action == mini_buttons.ButtonRangeAction.DIVIDE:
                changed_via_button = True
                new_value_abs /= 10

            if mini_buttons.show_zero_button():
                new_value_abs = 0.0
                changed_via_button = True

            # Display the slider
            imgui.set_next_item_width(slider_width)
            was_changed_recently = interval.was_changed_recently()
            if was_changed_recently:
                imgui.push_style_color(imgui.Col_.frame_bg_hovered.value, ImVec4(1, 0, 1, 1))
            changed_slider, new_value_abs = imgui.slider_float(
                "##" + label, new_value_abs, 0.0, interval.interval_max(), interval.format_string(is_positive)
            )
            if was_changed_recently:
                imgui.pop_style_color()
            interval.set_target_value(new_value_abs)

            if accept_negative:
                cur_pos = imgui.get_cursor_screen_pos()
                cur_pos.x -= hello_imgui.em_size(0.5)
                imgui.set_cursor_screen_pos(cur_pos)
                if mini_buttons.show_sign_button():
                    sign *= -1
                    changed_via_button = True
                cur_pos.x += hello_imgui.em_size(1.5)
                imgui.set_cursor_screen_pos(cur_pos)

            label = _str_until_double_hash(label)
            if len(label) > 0:
                imgui.text(label)

    changed = changed_slider or changed_via_button
    imgui.pop_id()
    imgui.end_group()
    return changed, new_value_abs * sign


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

    @staticmethod
    def _compute_power_of_ten(current_float_value: float) -> PowerOfTen:
        if current_float_value == 0.0:
            return PowerOfTen(1)
        abs_value = abs(current_float_value)
        return PowerOfTen(int(math.ceil(math.log10(abs_value))))

    def get_or_create(self, id_: int, current_float_value: float) -> PowerOfTen:
        if id_ not in self.power_of_ten:
            self.power_of_ten[id_] = self._compute_power_of_ten(current_float_value)
        return self.power_of_ten[id_]


_POWER_OF_TEN_CACHE = _PowerOfTenCache()


def slider_float_any_range_log_scale(
    label: str, v: float, accept_negative: bool = True, nb_displayed_digit: int = 4
) -> Tuple[bool, float]:
    slider_width = _get_slider_width()
    imgui.begin_group()
    imgui.push_id(label)
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
            action = mini_buttons.show_buttons_range(
                "Multiply range by 10" + tooltip_range, "Divide range by 10" + tooltip_range
            )
            if action == mini_buttons.ButtonRangeAction.MULTIPLY:
                power_of_ten += 1  # type: ignore
                _POWER_OF_TEN_CACHE.power_of_ten[imgui.get_id(label)] = power_of_ten
            elif action == mini_buttons.ButtonRangeAction.DIVIDE:
                power_of_ten -= 1  # type: ignore
                _POWER_OF_TEN_CACHE.power_of_ten[imgui.get_id(label)] = power_of_ten

            # Work around a bug in imgui: we need to display more digits for small values
            if v != 0:
                v_log = math.log10(math.fabs(v))
                nb_min_displayed_digit = -int(v_log) + 1
                if nb_displayed_digit < nb_min_displayed_digit:
                    nb_displayed_digit = nb_min_displayed_digit

            # Display the logarithmic slider
            imgui.set_next_item_width(slider_width)
            format_string = f"%.{nb_displayed_digit}g"
            changed, new_value = imgui.slider_float(
                "##" + label, v, min_value, max_value, format_string, imgui.SliderFlags_.logarithmic.value
            )
            label = _str_until_double_hash(label)
            if len(label) > 0:
                imgui.text(label)

    imgui.pop_id()
    imgui.end_group()
    return changed, new_value


def sandbox() -> None:
    value1 = 300.0
    value2 = 3.0

    value_log = 11.0
    value_log_positive = 1.0

    value_input = 4.0

    def gui() -> None:
        nonlocal value1, value2, value_log, value_log_positive, value_input
        changed, value1 = slider_float_any_range("slider_pos", value1, accept_negative=False)
        changed, value2 = slider_float_any_range("slider_pos_neg", value2)
        changed, value_log = slider_float_any_range_log_scale("slider_log", value_log)
        changed, value_log_positive = slider_float_any_range_log_scale(
            "slider_log_pos", value_log_positive, accept_negative=False
        )
        changed, value_input = imgui.input_float("input_float", value_input, step=0.1, step_fast=1.0)

    hello_imgui.run(gui)


if __name__ == "__main__":
    sandbox()
