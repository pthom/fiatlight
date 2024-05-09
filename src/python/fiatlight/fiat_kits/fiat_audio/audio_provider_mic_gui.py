"""AudioProviderMicGui is a FunctionWithGui that provides live audio from the microphone
under the form of SoundBlocksList. It is a GUI wrapper around the AudioProviderMic class."""

from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6, misc_widgets
from fiatlight.fiat_core import AnyDataWithGui
from imgui_bundle import imgui, imgui_ctx

from .audio_types import SoundStreamParams
from .audio_provider_mic import AudioProviderMic
from .audio_provider_gui import AudioProviderGui


class SoundStreamParamsGui(AnyDataWithGui[SoundStreamParams]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.default_value_provider = lambda: SoundStreamParams()
        self.callbacks.present_str = (
            lambda x: f"{x.sample_rate / 1000} kHz, {x.nb_channels} channels, {x.block_size} samples"
        )
        self.callbacks.edit = self.edit

    def edit(self) -> bool:
        from .audio_types_gui import SampleRateGui, BlockSizeGui

        value = self.get_actual_value()
        changed = False

        with imgui_ctx.begin_vertical("Params"):
            imgui.text("Sample Rate")
            sample_rate_gui = SampleRateGui()
            sample_rate_gui.value = value.sample_rate
            assert sample_rate_gui.callbacks.edit is not None
            if sample_rate_gui.callbacks.edit():
                value.sample_rate = sample_rate_gui.value
                changed = True

            # Disabled because some computers can only record in mono,
            # and trying to record with two channels will fail.
            #
            # imgui.text("Nb Channels")
            # nb_channels_gui = NbChannelsGui()
            # nb_channels_gui.value = value.nb_channels
            # assert nb_channels_gui.callbacks.edit is not None
            # if nb_channels_gui.callbacks.edit():
            #     value.nb_channels = nb_channels_gui.value
            #     changed = True

            imgui.text("Block Size")
            block_size_gui = BlockSizeGui()
            block_size_gui.value = value.block_size
            assert block_size_gui.callbacks.edit is not None
            if block_size_gui.callbacks.edit():
                value.block_size = block_size_gui.value
                changed = True

        return changed


class AudioProviderMicGui(AudioProviderGui):
    # Serialized options
    _microphone_params_gui: SoundStreamParamsGui
    # IO
    _microphone_io: AudioProviderMic

    def __init__(self) -> None:
        # Initialize the microphone
        self._microphone_params_gui = SoundStreamParamsGui()
        self._microphone_params_gui.value = SoundStreamParams()
        self._microphone_io = AudioProviderMic(self._microphone_params_gui.value)

        # FunctionWithGui init
        super().__init__(self._microphone_io)
        self.name = "AudioProviderMicGui"

    def specialized_internal_gui(self) -> bool:
        """Draw the internal GUI of the function (mic related)"""
        with fontawesome_6_ctx():
            is_started = self._microphone_io.started()
            imgui.begin_disabled(is_started)
            _params_changed = self._microphone_params_gui.edit()
            imgui.end_disabled()
            if misc_widgets.on_off_button_with_icons(
                is_started,
                icons_fontawesome_6.ICON_FA_MICROPHONE_LINES,
                icons_fontawesome_6.ICON_FA_MICROPHONE_LINES_SLASH,
            ):
                self._microphone_io.toggle()

        return False
