"""SoundWaveGui class for displaying SoundWave data in a GUI."""
import logging
from dataclasses import dataclass

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.demos.audio.sound_wave import SoundWave
from fiatlight.demos.audio.sound_wave_player import SoundWavePlayer
from imgui_bundle import implot, imgui, hello_imgui, imgui_ctx
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx, fiat_osd
from fiatlight.fiat_types import TimeSeconds, JsonDict


def button_with_disable_flag(label: str, is_disabled: bool) -> bool:
    if is_disabled:
        imgui.begin_disabled()
    clicked = imgui.button(label)
    if is_disabled:
        imgui.end_disabled()
    return clicked


@dataclass
class SoundWaveGuiParams:
    show_time_as_seconds: bool = False

    def to_dict(self) -> JsonDict:
        return {"show_time_as_seconds": self.show_time_as_seconds}

    def fill_from_dict(self, data: JsonDict) -> None:
        self.show_time_as_seconds = data.get("show_time_as_seconds", True)


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

    def _plot_waveform(self) -> None:
        sound_wave = self._sound_wave_gui_resampled
        if sound_wave is None:
            return
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
