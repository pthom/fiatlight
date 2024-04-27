"""SoundWaveGui class for displaying SoundWave data in a GUI."""
import logging
from dataclasses import dataclass

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.demos.audio.sound_wave import SoundWave
from fiatlight.demos.audio.sound_wave_player import SoundWavePlayer
from imgui_bundle import implot, imgui, hello_imgui, imgui_ctx, ImVec2
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx, fiat_osd, button_with_disable_flag
from fiatlight.fiat_types import TimeSeconds, JsonDict
from fiatlight.fiat_utils import fiat_math


@dataclass(frozen=True)
class SoundWaveSelection:
    start: TimeSeconds = TimeSeconds(-1)
    end: TimeSeconds = TimeSeconds(-1)

    def is_empty(self) -> bool:
        return self.start == -1 or self.end == -1  # type: ignore

    def to_dict(self) -> JsonDict:
        return {
            "start": self.start,
            "end": self.end,
        }

    @staticmethod
    def from_dict(data: JsonDict) -> "SoundWaveSelection":
        start = data["start"]
        end = data["end"]
        return SoundWaveSelection(start, end)


@dataclass
class SoundWaveGuiParams:
    show_time_as_seconds: bool = False
    can_select: bool = False
    selection: SoundWaveSelection = SoundWaveSelection()

    def to_dict(self) -> JsonDict:
        return {
            "show_time_as_seconds": self.show_time_as_seconds,
            "can_select": self.can_select,
            "selection": self.selection.to_dict() if self.selection is not None else None,
        }

    def fill_from_dict(self, data: JsonDict) -> None:
        self.show_time_as_seconds = data.get("show_time_as_seconds", True)
        self.can_select = data.get("can_select", False)
        selection_data = data["selection"]
        self.selection = SoundWaveSelection.from_dict(selection_data)


class SoundWaveGui(AnyDataWithGui[SoundWave]):
    """SoundWaveGui: a FunctionWithGui that displays a SoundWave in a GUI, with playback controls."""

    params: SoundWaveGuiParams = SoundWaveGuiParams()
    _sound_wave_player: SoundWavePlayer | None = None
    # A sound wave with fewer samples, for faster plotting
    _sound_wave_gui_resampled: SoundWave | None = None

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.present_custom = self.present_custom
        self.callbacks.on_change = self._on_change
        self.callbacks.on_exit = self._on_exit
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

    def save_gui_options_to_json(self) -> JsonDict:
        return self.params.to_dict()

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        self.params.fill_from_dict(data)

    def _on_change(self) -> None:
        if self._sound_wave_player is not None:
            self._sound_wave_player.stop()
            self._sound_wave_player = None
        sound_wave = self.get_actual_value()
        self._sound_wave_gui_resampled = sound_wave._rough_resample_to_max_samples(max_samples=1000)
        self._sound_wave_player = SoundWavePlayer(sound_wave)
        selection_start = TimeSeconds(sound_wave.duration() * 0.25)
        selection_end = TimeSeconds(sound_wave.duration() * 0.75)
        self.params.selection = SoundWaveSelection(selection_start, selection_end)

    def _on_exit(self) -> None:
        if self._sound_wave_player is not None:
            logging.warning("SoundWaveGui: stopping player on exit")
            self._sound_wave_player.stop()
            self._sound_wave_player = None

    def _show_controls(self) -> None:
        assert self._sound_wave_player is not None
        with imgui_ctx.begin_horizontal("Controls"):
            with fontawesome_6_ctx():
                small_step = TimeSeconds(0.1)
                large_step = TimeSeconds(5.0)

                if imgui.button(icons_fontawesome_6.ICON_FA_BACKWARD_FAST):
                    self._sound_wave_player.seek(TimeSeconds(0))
                fiat_osd.set_widget_tooltip("Rewind to start (hold to seek fast)")

                with imgui_ctx.push_button_repeat():
                    can_rewind_large = self._sound_wave_player.can_rewind(large_step)
                    if button_with_disable_flag(
                        icons_fontawesome_6.ICON_FA_BACKWARD_STEP + "##large", not can_rewind_large
                    ):
                        self._sound_wave_player.rewind(large_step)
                    fiat_osd.set_widget_tooltip(f"Rewind {large_step}s (hold to seek fast)")

                    can_rewind_small = self._sound_wave_player.can_rewind(small_step)
                    if button_with_disable_flag(
                        icons_fontawesome_6.ICON_FA_BACKWARD_STEP + "##small", not can_rewind_small
                    ):
                        self._sound_wave_player.rewind(small_step)
                    fiat_osd.set_widget_tooltip(f"Rewind {small_step}s (hold to seek fast)")

                if self._sound_wave_player.is_playing():
                    if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_PAUSE):
                        self._sound_wave_player.pause()
                    fiat_osd.set_widget_tooltip("Pause")
                else:
                    if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_PLAY):
                        self._sound_wave_player.play()
                    fiat_osd.set_widget_tooltip("Play")

                with imgui_ctx.push_button_repeat():
                    can_advance_small = self._sound_wave_player.can_advance(small_step)
                    if button_with_disable_flag(
                        icons_fontawesome_6.ICON_FA_FORWARD_STEP + "##small", not can_advance_small
                    ):
                        self._sound_wave_player.advance(small_step)
                    fiat_osd.set_widget_tooltip(f"Advance {small_step}s (hold to seek fast)")

                    can_advance_large = self._sound_wave_player.can_advance(large_step)
                    if button_with_disable_flag(
                        icons_fontawesome_6.ICON_FA_FORWARD_STEP + "##large", not can_advance_large
                    ):
                        self._sound_wave_player.advance(large_step)
                    fiat_osd.set_widget_tooltip(f"Advance {large_step}s (hold to seek fast)")

                if imgui.button(icons_fontawesome_6.ICON_FA_FORWARD_FAST):
                    self._sound_wave_player.seek(TimeSeconds(self._sound_wave_player.sound_wave.duration()))
                fiat_osd.set_widget_tooltip("Fast forward to end")

    def _format_time(self, timepoint: TimeSeconds) -> str:
        sound_wave = self.get_actual_value()
        from fiatlight.fiat_types import format_time_seconds_as_hh_mm_ss_cc, format_time_seconds_as_mm_ss_cc

        if self.params.show_time_as_seconds:
            return f"{timepoint:.2f}s"
        else:
            is_longer_than_1_hour = sound_wave.duration() >= 3600
            if is_longer_than_1_hour:
                return format_time_seconds_as_hh_mm_ss_cc(timepoint)
            else:
                return format_time_seconds_as_mm_ss_cc(timepoint)

    def _show_position(self) -> None:
        assert self._sound_wave_player is not None
        sound_wave = self.get_actual_value()
        with imgui_ctx.begin_horizontal("Position"):
            # Use springs to center the text
            imgui.spring()
            position = self._sound_wave_player.position_seconds()
            duration = sound_wave.duration()
            imgui.text(f"{self._format_time(position)} / {self._format_time(duration)}")
            imgui.spring()
            _, self.params.show_time_as_seconds = imgui.checkbox("seconds", self.params.show_time_as_seconds)

    def _plot_selection(self) -> None:
        sound_wave = self._sound_wave_gui_resampled
        if sound_wave is None:
            return
        selection_line_color = imgui.ImVec4(0.0, 1.0, 0.0, 1.0)

        def draw_selection_bg() -> None:
            if self.params.selection is None:
                return
            selection_bg_color = imgui.ImVec4(0.0, 1.0, 0.0, 0.2)
            selection_bg_color2 = imgui.color_convert_float4_to_u32(selection_bg_color)
            pos = implot.get_plot_pos()
            size = implot.get_plot_size()
            y1 = pos.y
            y2 = pos.y + size.y
            k1 = fiat_math.unlerp(0, sound_wave.duration(), self.params.selection.start)
            k2 = fiat_math.unlerp(0, sound_wave.duration(), self.params.selection.end)
            x1 = fiat_math.lerp(pos.x, pos.x + size.x, k1)
            x2 = fiat_math.lerp(pos.x, pos.x + size.x, k2)
            tl = ImVec2(x1, y1)
            br = ImVec2(x2, y2)
            implot.get_plot_draw_list().add_rect_filled(tl, br, selection_bg_color2)

        draw_selection_bg()

        if self.params.selection is None:
            return

        sel_start = self.params.selection.start
        changed_1, new_sel_start, clicked, hovered, held = implot.drag_line_x(1, sel_start, selection_line_color)

        sel_end = self.params.selection.end
        changed_2, new_sel_end, clicked, hovered, held = implot.drag_line_x(2, sel_end, selection_line_color)

        if changed_1 or changed_2:
            if new_sel_end < new_sel_start:
                new_sel_end, new_sel_start = new_sel_start, new_sel_end
            new_sel_start = fiat_math.clamp(new_sel_start, 0, sound_wave.duration())
            new_sel_end = fiat_math.clamp(new_sel_end, 0, sound_wave.duration())
            self.params.selection = SoundWaveSelection(new_sel_start, new_sel_end)  # type: ignore

    def _plot_waveform(self) -> None:
        sound_wave = self._sound_wave_gui_resampled
        if sound_wave is None:
            return

        select_change, self.params.can_select = imgui.checkbox("Select", self.params.can_select)

        plot_size = hello_imgui.em_to_vec2(20, 10)
        if implot.begin_plot("##Audio Waveform", plot_size):
            implot.setup_axes(
                "Time [s]", "Amplitude", implot.AxisFlags_.auto_fit.value, implot.AxisFlags_.auto_fit.value
            )

            # Add line / position
            if self._sound_wave_player is not None:
                x = self._sound_wave_player.position_seconds()
                line_color = imgui.ImVec4(1.0, 0.0, 0.0, 1.0)
                changed, new_x, clicked, hovered, held = implot.drag_line_x(0, x, line_color)
                if changed:
                    self._sound_wave_player.seek(TimeSeconds(new_x))

            # Add rect / selection
            if self._sound_wave_player is not None and self.params.can_select:
                self._plot_selection()

            implot.plot_line("##Waveform", sound_wave.time_array(), sound_wave.wave)
            implot.end_plot()

    def present_custom(self) -> None:
        sound_wave = self.get_actual_value()
        imgui.text(f"Duration: {sound_wave.duration():.2f} s, Sample Rate: {sound_wave.sample_rate} Hz")
        self._plot_waveform()

        if self._sound_wave_player is not None:
            with imgui_ctx.begin_vertical("ControlsAndPosition"):
                self._show_controls()
                self._show_position()
