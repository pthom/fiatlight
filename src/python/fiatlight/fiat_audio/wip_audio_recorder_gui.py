import fiatlight.fiat_core.composite_gui
from fiatlight.fiat_audio.audio_types_gui import SoundBlocksListGui
from fiatlight.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui
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
    recording_status: RecordingStatus = RecordingStatus.NotRecording

    # Output after recording
    _sound_wave: SoundWave | None = None

    def __init__(self) -> None:
        super().__init__(self._f)
        self.name = "AudioRecorderGui"
        self.internal_state_gui = self._internal_gui

        # Input and output GUI
        self.add_param("sound_blocks_list", SoundBlocksListGui())
        output_gui = fiatlight.fiat_core.composite_gui.OptionalWithGui(SoundWavePlayerGui())
        self.add_output(output_gui)

    def _f(self, sound_blocks_list: SoundBlocksList) -> SoundWave | None:
        """This is the function in itself.
        It returns None during before/during the recording, and the full SoundWave after the recording."""
        self._store_sound_blocks(sound_blocks_list)

        return self._sound_wave

    def _display_control_buttons(self) -> None:
        with imgui_ctx.begin_horizontal("RecordingControls"):
            button_size = hello_imgui.em_to_vec2(3, 3)
            with fontawesome_6_ctx():
                if self.recording_status == RecordingStatus.NotRecording:
                    if imgui.button(icons_fontawesome_6.ICON_FA_RECORD_VINYL, button_size):
                        self.recording_status = RecordingStatus.Recording
                        self._on_start_recording()
                elif self.recording_status == RecordingStatus.Recording:
                    if imgui.button(icons_fontawesome_6.ICON_FA_PAUSE, button_size):
                        self.recording_status = RecordingStatus.Paused
                        self._on_pause_recording()
                    if imgui.button(icons_fontawesome_6.ICON_FA_STOP, button_size):
                        self.recording_status = RecordingStatus.NotRecording
                        self._on_stop_recording()
                elif self.recording_status == RecordingStatus.Paused:
                    if imgui.button(icons_fontawesome_6.ICON_FA_PLAY, button_size):
                        self.recording_status = RecordingStatus.Recording
                        self._on_start_recording()
                    if imgui.button(icons_fontawesome_6.ICON_FA_STOP, button_size):
                        self.recording_status = RecordingStatus.NotRecording
                        self._on_stop_recording()

    def _internal_gui(self) -> bool:
        """Draw the internal GUI of the function."""
        with imgui_ctx.begin_vertical("AudioRecorderGui"):
            self._display_control_buttons()
            if self._sound_wave_being_recorded is not None:
                nb_samples = self._sound_wave_being_recorded.wave.shape[0]
                imgui.text(f"Recording in progress: ({nb_samples} samples)")

        return False

    def _on_start_recording(self) -> None:
        self._sound_wave = None
        self._recording_status = RecordingStatus.Recording

    def _on_pause_recording(self) -> None:
        self.recording_status = RecordingStatus.Paused

    def _on_stop_recording(self) -> None:
        self._sound_wave = self._sound_wave_being_recorded
        self._sound_wave_being_recorded = None
        self._was_recording_just_stopped = True
        self._recording_status = RecordingStatus.NotRecording

    def _store_sound_blocks(self, sound_blocks_list: SoundBlocksList) -> None:
        if self.recording_status == RecordingStatus.Recording:
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


if __name__ == "__main__":
    sandbox_audio_recorder_gui()
