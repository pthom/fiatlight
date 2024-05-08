import logging

from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_audio.audio_types import SoundWave, SoundBlocksList
from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx
from imgui_bundle import imgui_ctx, imgui, hello_imgui
from enum import Enum
import numpy as np


class RecordingStatus(Enum):
    NotRecording = 1
    Recording = 2
    Paused = 3


class AudioRecorderGui(FunctionWithGui):
    # Output being recorded
    _sound_wave_being_recorded: SoundWave | None = None
    _recording_status: RecordingStatus = RecordingStatus.NotRecording

    # Output after recording
    _sound_wave: SoundWave | None = None

    _shall_append: bool = False

    def __init__(self) -> None:
        super().__init__(self._f, "AudioRecorderGui")
        self.internal_state_gui = self._internal_gui

    def _f(self, sound_blocks_list: SoundBlocksList) -> SoundWave | None:
        """This is the function in itself.
        It returns None during before/during the recording, and the full SoundWave after the recording."""
        self._store_sound_blocks(sound_blocks_list)

        return self._sound_wave

    def _display_control_buttons(self) -> None:
        with imgui_ctx.begin_horizontal("RecordingControls"):
            button_size = hello_imgui.em_to_vec2(3, 3)
            with fontawesome_6_ctx():
                # Two buttons, in this order:
                #   [Play/Pause] [Stop, may be disabled]

                # [Play / Pause]
                if (
                    self._recording_status == RecordingStatus.NotRecording
                    or self._recording_status == RecordingStatus.Paused
                ):
                    if imgui.button(icons_fontawesome_6.ICON_FA_RECORD_VINYL, button_size):
                        self._recording_status = RecordingStatus.Recording
                        self._on_start_recording()
                elif self._recording_status == RecordingStatus.Recording:
                    if imgui.button(icons_fontawesome_6.ICON_FA_PAUSE, button_size):
                        self._recording_status = RecordingStatus.Paused
                        self._on_pause_recording()

                # [Stop]
                is_disabled = self._recording_status == RecordingStatus.NotRecording
                imgui.begin_disabled(is_disabled)
                if imgui.button(icons_fontawesome_6.ICON_FA_STOP, button_size):
                    self._on_stop_recording()
                imgui.end_disabled()

            imgui.spring()

    def _internal_gui(self) -> bool:
        """Draw the internal GUI of the function."""
        changed = False
        with imgui_ctx.begin_vertical("AudioRecorderGui"):
            self._display_control_buttons()
            _, self._shall_append = imgui.checkbox("Append", self._shall_append)

            if self._sound_wave_being_recorded is not None:
                nb_samples = self._sound_wave_being_recorded.wave.shape[0]
                imgui.text(f"Recording in progress: ({nb_samples} samples)")

            if self._sound_wave is not None and self._recording_status == RecordingStatus.NotRecording:
                if imgui.button("Clear"):
                    self._sound_wave = None
                    changed = True

        return changed

    def _on_start_recording(self) -> None:
        logging.info("_on_start_recording")
        if not self._shall_append:
            self._sound_wave = None
        self._recording_status = RecordingStatus.Recording

    def _on_pause_recording(self) -> None:
        logging.info("_on_pause_recording")
        self._recording_status = RecordingStatus.Paused

    def _on_stop_recording(self) -> None:
        self._recording_status = RecordingStatus.NotRecording
        if self._sound_wave_being_recorded is None:
            return
        logging.info(
            f"{self._shall_append=} _sound_wave:{self._sound_wave is not None} rec:{self._sound_wave_being_recorded is not None}"
        )
        if self._shall_append and self._sound_wave is not None:
            logging.info("_on_stop_recording => concat")
            new_wave = np.concatenate([self._sound_wave.wave, self._sound_wave_being_recorded.wave])
            self._sound_wave = SoundWave(new_wave, self._sound_wave.sample_rate)  # type: ignore
        else:
            logging.info("_on_stop_recording => new")
            self._sound_wave = self._sound_wave_being_recorded

        self._sound_wave_being_recorded = None

    def _store_sound_blocks(self, sound_blocks_list: SoundBlocksList) -> None:
        if self._recording_status == RecordingStatus.Recording:
            for sound_block in sound_blocks_list.blocks:
                if self._sound_wave_being_recorded is None:
                    sample_rate = sound_blocks_list.sample_rate
                    self._sound_wave_being_recorded = SoundWave(sound_block, sample_rate)  # type: ignore
                else:
                    self._sound_wave_being_recorded.wave = np.concatenate(
                        [self._sound_wave_being_recorded.wave, sound_block]
                    )


def sandbox_audio_recorder_gui() -> None:
    import fiatlight
    from fiatlight.fiat_audio.wip_microphone_gui import MicrophoneGui

    microphone_gui = MicrophoneGui()
    audio_recorder_gui = AudioRecorderGui()

    fiatlight.fiat_run_composition([microphone_gui, audio_recorder_gui])


# def sandbox_audio_recorder_gui_with_freq_display() -> None:
#     def find_dominant_frequency(signal, sample_rate):  # type: ignore
#         import numpy as np
#         from scipy.fft import fft  # type: ignore
#
#         signal_fft = fft(signal)
#         magnitudes = np.abs(signal_fft)
#         # Exclude the zero frequency "DC component" for finding the maximum
#         positive_frequencies = magnitudes[:len(magnitudes) // 2]
#         # Find the frequency with the maximum magnitude
#         peak_frequency = np.argmax(positive_frequencies)
#         # Convert the index of the maximum frequency component to an actual frequency
#         dominant_frequency = peak_frequency * sample_rate / len(signal)
#         return dominant_frequency
#
#     def find_dom_freq(block_list: SoundBlocksList) -> str:
#         if len(block_list.blocks) == 0:
#             return "0.0"
#         sound_block = block_list.blocks[-1]
#         dom_freq = find_dominant_frequency(sound_block, block_list.sample_rate) # type: ignore
#         return f"Dominant frequency: {dom_freq:.1f} Hz"
#
#     import fiatlight
#     graph = fiatlight.FunctionsGraph()
#     from fiatlight.fiat_audio.wip_microphone_gui import MicrophoneGui
#     # microphone_gui = MicrophoneGui()
#     # audio_recorder_gui = AudioRecorderGui()
#     graph.add_function_composition([AudioRecorderGui(), MicrophoneGui()])
#     graph.add_function(find_dom_freq)
#     graph.add_link("MicrophoneGui", "find_dom_freq")
#     fiatlight.fiat_run_graph(graph)


if __name__ == "__main__":
    sandbox_audio_recorder_gui()
    # sandbox_audio_recorder_gui_with_freq_display()
