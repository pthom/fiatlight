# """AudioProviderMicGui is a FunctionWithGui that provides live audio from the microphone
# under the form of SoundBlocksList. It is a GUI wrapper around the AudioProviderMic class."""
#
# from imgui_bundle import imgui
# from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6, misc_widgets
#
# from fiatlight.fiat_kits.fiat_audio.audio_provider_mic import AudioProviderMic
# from fiatlight.fiat_kits.fiat_audio.old2.audio_provider_gui import AudioProviderGui
# from fiatlight.fiat_kits.fiat_audio.audio_types import SoundStreamParams
# from fiatlight.fiat_kits.fiat_audio.audio_types_gui import SoundStreamParamsGui
#
#
# class AudioProviderMicGui(AudioProviderGui):
#     # IO
#     _mic_provider: AudioProviderMic
#     # Serialized options
#     _mic_stream_params_gui: SoundStreamParamsGui
#
#     def __init__(self) -> None:
#         # Initialize the microphone
#         self._mic_provider = AudioProviderMic()
#
#         # FunctionWithGui init
#         super().__init__(self._mic_provider)
#         self.name = "AudioProviderMicGui"
#
#         # Initialize the sound stream params GUI: TODO make it easy to create AnyDataWithGui with a linked value
#         self._mic_stream_params_gui = SoundStreamParamsGui()
#         self._mic_stream_params_gui.value = SoundStreamParams()
#
#     def specialized_internal_gui(self) -> bool:
#         """Draw the internal GUI of the function (mic related)"""
#         with fontawesome_6_ctx():
#             is_started = self._mic_provider.started()
#
#             # Edit the sound stream params (only if the audio provider is not started)
#             imgui.begin_disabled(is_started)
#             _changed_stream_params = self._mic_stream_params_gui.edit()
#             imgui.end_disabled()
#
#             if misc_widgets.on_off_button_with_icons(
#                 is_started,
#                 icons_fontawesome_6.ICON_FA_MICROPHONE_LINES,
#                 icons_fontawesome_6.ICON_FA_MICROPHONE_LINES_SLASH,
#             ):
#                 stream_params = self._mic_stream_params_gui.get_actual_value()
#                 self._mic_provider.toggle(stream_params)
#
#         return False
