from imgui_bundle import imgui, ImVec4, imgui_ctx, hello_imgui
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import fontawesome_6_ctx
from typing import Dict, Tuple
import time
import math


class _SliderAdaptiveInterval:
    nb_significant_digits: int = 4
    current_power: int = 1
    time_last_power_change: float = 0.0

    def __init__(self, nb_significant_digits: int = 4) -> None:
        self.nb_significant_digits = nb_significant_digits

    def interval_max(self) -> float:
        return math.pow(10, self.current_power)

    def set_target_value(self, target_value: float) -> None:
        assert target_value >= 0.0

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


class _SliderAdaptiveIntervalCache:
    intervals: Dict[int, _SliderAdaptiveInterval]

    def __init__(self) -> None:
        self.intervals = {}

    def get_or_create(self, id: int, nb_significant_digits: int) -> _SliderAdaptiveInterval:
        if id not in self.intervals:
            self.intervals[id] = _SliderAdaptiveInterval(nb_significant_digits)
        return self.intervals[id]


_SLIDER_ADAPTIVE_INTERVAL_CACHE = _SliderAdaptiveIntervalCache()


def slider_any_positive_float(label: str, v: float, nb_significant_digits: int = 4) -> Tuple[bool, float]:
    """A slider that can edit *positive* floats, with a given number of significant digits
    for any value (the slider will interactively adapt its range to the value,
    and flash red when the range changed)
    """
    from fiatlight.fiat_widgets import fiat_osd

    global _SLIDER_ADAPTIVE_INTERVAL_CACHE
    float32_max = 3.4028234663852886e38
    max_value = float32_max / 10
    if v > max_value:
        v = max_value
        return True, v

    label_id = imgui.get_id(label)
    interval = _SLIDER_ADAPTIVE_INTERVAL_CACHE.get_or_create(label_id, nb_significant_digits)

    with imgui_ctx.begin_horizontal(label):
        with imgui_ctx.push_id(str(interval.current_power)):
            was_changed_recently = interval.was_changed_recently()
            if was_changed_recently:
                imgui.push_style_color(imgui.Col_.frame_bg_hovered.value, ImVec4(1, 0, 0, 1))
            changed, new_value = imgui.slider_float(label, v, 0.0, interval.interval_max(), interval.format_string())
            if was_changed_recently:
                imgui.pop_style_color()
            interval.set_target_value(new_value)

            with fontawesome_6_ctx():
                orig_cursor_pos = imgui.get_cursor_pos()
                cur_pos = imgui.get_cursor_pos()
                cur_pos.x -= hello_imgui.em_size(0.5)
                imgui.set_cursor_pos(cur_pos)

                btn_size = hello_imgui.em_to_vec2(0.7, 0.65)
                if imgui.button("##+", btn_size):
                    changed = True
                    new_value *= 10
                fiat_osd.set_widget_tooltip("Multiply by 10")
                cur_pos.y += hello_imgui.em_size(0.7)
                imgui.set_cursor_pos(cur_pos)
                if imgui.button("##-", btn_size):
                    changed = True
                    new_value /= 10
                fiat_osd.set_widget_tooltip("Divide by 10")

                final_cursor_pos = orig_cursor_pos
                final_cursor_pos.x += hello_imgui.em_size(3.0)
                imgui.set_cursor_pos(final_cursor_pos)

    return changed, new_value


def sandbox() -> None:
    from imgui_bundle import hello_imgui

    value1 = 300.0
    value2 = 3.0

    def gui() -> None:
        nonlocal value1, value2
        changed, value1 = slider_any_positive_float("##slider", value1)
        changed, value2 = slider_any_positive_float("##slider2", value2)

    hello_imgui.run(gui)


if __name__ == "__main__":
    sandbox()
