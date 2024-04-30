# from fiatlight.fiat_core.function_with_gui import FunctionWithGui
# from fiatlight.fiat_audio.audio_types import SoundBlock, SoundWave
#
#
# class AudioRecorderGui(FunctionWithGui):
#     # Output being recorded
#     _sound_wave_being_recorded: SoundBlock | None = None
#     _is_recording: bool = False
#
#     # Output after recording
#     _sound_wave: SoundWave | None = None
#     _was_recording_just_stopped: bool = False
#
#     def _on_start_recording(self) -> None:
#         self._sound_wave = None
#         self._is_recording = True
#
#     def _on_stop_recording(self) -> None:
#         self._sound_wave = SoundWave(self._sound_wave_being_recorded, self._microphone_params_gui.value.sample_rate)  # type: ignore
#         self._was_recording_just_stopped = True
#         self._is_recording = False
#
#     def _f(self) -> SoundWave:
#         assert self._sound_wave is not None
#         return self._sound_wave
#
#     def _on_heartbeat(self) -> bool:
#         sound_blocks = self._microphone_io.get_sound_blocks()
#
#         # Display the last sound block
#         if len(sound_blocks) > 0:
#             self._displayed_sound_block = sound_blocks[-1]
#
#         # Append sound blocks to the recording
#         if self._is_recording:
#             for sound_block in sound_blocks:
#                 if self._sound_wave_being_recorded is None:
#                     self._sound_wave_being_recorded = sound_block
#                 else:
#                     self._sound_wave_being_recorded = np.concatenate([self._sound_wave_being_recorded, sound_block])
#
#         # Trigger a call to self._f() if the recording was just stopped
#         needs_refresh = self._was_recording_just_stopped
#         self._was_recording_just_stopped = False
#         return needs_refresh
