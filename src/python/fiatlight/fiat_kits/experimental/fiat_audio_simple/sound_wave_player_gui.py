"""SoundWavePlayerGui class for displaying and playing SoundWave data in a GUI.

This version might be refactored in the future since it mixes the sound source and the play & display part.
"""

import logging
from dataclasses import dataclass

from imgui_bundle import hello_imgui
from imgui_bundle import implot, imgui, imgui_ctx, ImVec2, immapp

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_widgets import (
    icons_fontawesome_6,
    fontawesome_6_ctx,
    fiat_osd,
    button_with_disable_flag,
)
from fiatlight.fiat_types import TimeSeconds, JsonDict
from numpy.typing import NDArray
import numpy as np

from .audio_types import SoundWave
from .sound_wave_player import SoundWavePlayer


def _downsample_wave_minmax(wave: np.ndarray, max_samples: int) -> np.ndarray:
    """Downsample using min/max strategy for plotting.
    Alternates between min and max per chunk, to simulate waveform spikes.
    Only supports 1D arrays (flattened audio channel)."""
    assert wave.ndim == 1
    if len(wave) <= max_samples:
        return wave

    chunk_size = int(np.ceil(len(wave) / max_samples))
    downsampled = []
    use_min = True

    for i in range(0, len(wave), chunk_size):
        chunk = wave[i : i + chunk_size]
        val = chunk.min() if use_min else chunk.max()
        downsampled.append(val)
        use_min = not use_min

    return np.array(downsampled)


@dataclass
class SoundWaveGuiParams:
    plot_size_em: ImVec2 | None = None
    show_time_as_seconds: bool = False
    volume: float = 1.0

    def __post_init__(self) -> None:
        if self.plot_size_em is None:
            self.plot_size_em = ImVec2(20, 10)

    def to_dict(self) -> JsonDict:
        assert self.plot_size_em is not None
        return {
            "show_time_as_seconds": self.show_time_as_seconds,
            "volume": self.volume,
            "plot_size_em": [self.plot_size_em.x, self.plot_size_em.y],
        }

    def fill_from_dict(self, data: JsonDict) -> None:
        self.show_time_as_seconds = data.get("show_time_as_seconds", True)
        self.volume = data.get("volume", 1.0)
        plot_size_array = data.get("plot_size_em", [20, 10])
        self.plot_size_em = ImVec2(plot_size_array[0], plot_size_array[1])


class SoundWavePlayerGui(AnyDataWithGui[SoundWave]):
    """SoundWavePlayerGui: a FunctionWithGui that displays a SoundWave in a GUI, with playback controls."""

    params: SoundWaveGuiParams
    _sound_wave_player: SoundWavePlayer | None = None
    # Sound wave per channel, with fewer samples, for faster plotting
    _plotted_values: list[NDArray[np.float32]] | None = None
    _plotted_times: NDArray[np.float32] | None = None

    def __init__(self) -> None:
        super().__init__(SoundWave)
        self.params = SoundWaveGuiParams()
        self.callbacks.present = self.present
        self.callbacks.on_change = self._on_change
        self.callbacks.on_exit = self._on_exit
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

    def save_gui_options_to_json(self) -> JsonDict:
        return self.params.to_dict()

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        self.params.fill_from_dict(data)

    def _on_change(self, sound_wave: SoundWave) -> None:
        if self._sound_wave_player is not None:
            is_same_wave = self._sound_wave_player.sound_wave is sound_wave
            if is_same_wave:
                # logging.info("SoundWavePlayerGui.on_change(): same sound wave, not changing")
                return
        if self._sound_wave_player is not None:
            self._sound_wave_player.stop()
            self._sound_wave_player = None
        if sound_wave.is_empty():
            return

        self._cache_plotted_wave(sound_wave)

        self._sound_wave_player = SoundWavePlayer(sound_wave)

    def _cache_plotted_wave(self, sound_wave: SoundWave):
        width_pixels = self.params.plot_size_em.x * hello_imgui.em_size()
        max_samples_on_plot = int(width_pixels * 4)
        self._plotted_values = []
        from .audio_types import extract_flattened_channel

        for channel in range(sound_wave.nb_channels()):
            channel_wave = extract_flattened_channel(sound_wave.wave, channel)
            downsampled_wave = _downsample_wave_minmax(channel_wave, max_samples_on_plot)
            self._plotted_values.append(downsampled_wave)
        start = 0
        stop = sound_wave.duration()
        step = (stop - start) / max_samples_on_plot
        self._plotted_times = np.arange(start=start, stop=stop, step=step, dtype=np.float32)

    def _on_exit(self) -> None:
        if self._sound_wave_player is not None:
            logging.warning("SoundWavePlayerGui: stopping player on exit")
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
        from fiatlight.fiat_types import format_time_seconds

        if self.params.show_time_as_seconds:
            return f"{timepoint:.2f}s"
        else:
            return format_time_seconds(timepoint, show_centiseconds=True)

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
        if self._plotted_values is None:
            return

        x_axis_flags = implot.AxisFlags_.auto_fit.value
        y_axis_flags = implot.AxisFlags_.auto_fit.value
        x_label = "Time [s]" if self.params.show_time_as_seconds else "Time"
        implot.setup_axes(x_label, "Amplitude", x_axis_flags, y_axis_flags)

        if not self.params.show_time_as_seconds:
            implot.get_style().use24_hour_clock = True
            implot.setup_axis_scale(implot.ImAxis_.x1.value, implot.Scale_.time.value)

        # nice channel colors:
        channel_colors = [
            imgui.ImVec4(0.20, 0.60, 1.00, 0.8),  # Soft Blue
            imgui.ImVec4(0.10, 0.90, 0.50, 0.8),  # Mint Green
            imgui.ImVec4(0.90, 0.40, 0.70, 1.0),  # Rose
            imgui.ImVec4(1.00, 0.80, 0.30, 1.0),  # Warm Yellow
            imgui.ImVec4(1.00, 0.45, 0.45, 1.0),  # Soft Coral
        ]
        for channel in range(len(self._plotted_values)):
            implot.push_style_color(implot.Col_.line.value, channel_colors[channel % len(channel_colors)])
            implot.plot_line(f"Channel {channel}", self._plotted_times, self._plotted_values[channel])
            implot.pop_style_color()

        # Add line / position
        if self._sound_wave_player is not None:
            x = self._sound_wave_player.position_seconds()
            line_color = imgui.ImVec4(1.0, 0.0, 0.0, 1.0)
            changed, new_x, clicked, hovered, held = implot.drag_line_x(0, x, line_color)
            if changed:
                self._sound_wave_player.seek(TimeSeconds(new_x))

    def present(self, sound_wave: SoundWave) -> None:
        imgui.text(
            f"Duration: {sound_wave.duration():.2f} s, Sample Rate: {sound_wave.sample_rate} Hz, Channels: {sound_wave.nb_channels()}"
        )
        imgui.set_next_item_width(hello_imgui.em_size(10))
        _, self.params.volume = imgui.slider_float("Volume", self.params.volume, 0.0, SoundWavePlayer.VOLUME_MAX)

        # _, self.params.can_select = imgui.checkbox("Select", self.params.can_select)
        assert self.params.plot_size_em is not None
        plot_size_pixels = immapp.em_to_vec2(self.params.plot_size_em)
        new_plot_size_pixels = immapp.show_resizable_plot_in_node_editor(
            "Audio Waveform", plot_size_pixels, self._plot_waveform
        )
        self.params.plot_size_em = immapp.pixels_to_em(new_plot_size_pixels)

        if self._sound_wave_player is not None:
            self._sound_wave_player.volume = self.params.volume
            with imgui_ctx.begin_vertical("ControlsAndPosition"):
                self._show_controls()
                self._show_position()
