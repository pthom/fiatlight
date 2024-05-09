"""Gui for simple types in fiat_audio.audio_types"""
from imgui_bundle import imgui, imgui_ctx
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_togui import make_explained_value_edit_callback
from .audio_types import (
    SampleRate,
    SampleRatesExplained,
    NbChannels,
    NbChannelsExplained,
    BlockSize,
    BlockSizesExplained,
    SoundBlocksList,
    SoundStreamParams,
)


class SampleRateGui(AnyDataWithGui[SampleRate]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = make_explained_value_edit_callback("sample_rate", self, SampleRatesExplained)
        self.callbacks.default_value_provider = lambda: SampleRate(44100)
        self.callbacks.present_str = lambda x: f"{x / 1000} kHz"


class NbChannelsGui(AnyDataWithGui[NbChannels]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = make_explained_value_edit_callback("nb_channels", self, NbChannelsExplained)
        self.callbacks.default_value_provider = lambda: NbChannels(1)
        self.callbacks.present_str = lambda x: "Mono" if x == 1 else "Stereo"


class BlockSizeGui(AnyDataWithGui[BlockSize]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = make_explained_value_edit_callback("block_size", self, BlockSizesExplained)
        self.callbacks.default_value_provider = lambda: BlockSize(1024)
        self.callbacks.present_str = lambda x: f"{x} samples"


class SoundBlocksListGui(AnyDataWithGui[SoundBlocksList]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.present_str = self._present_str

    @staticmethod
    def _present_str(value: SoundBlocksList) -> str:
        return f"{len(value.blocks)} blocks at {value.sample_rate / 1000:.1f} kHz"


class SoundStreamParamsGui(AnyDataWithGui[SoundStreamParams]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.default_value_provider = lambda: SoundStreamParams()
        self.callbacks.present_str = (
            lambda x: f"{x.sample_rate / 1000} kHz, {x.nb_channels} channels, {x.block_size} samples"
        )
        self.callbacks.edit = self.edit

    def edit(self) -> bool:
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


def register_audio_types_gui() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(SampleRate, SampleRateGui)
    register_type(NbChannels, NbChannelsGui)
    register_type(BlockSize, BlockSizeGui)
    register_type(SoundBlocksList, SoundBlocksListGui)
