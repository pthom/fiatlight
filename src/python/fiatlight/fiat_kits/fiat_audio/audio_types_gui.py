"""Gui for simple types in fiat_audio.audio_types"""
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_togui import make_explained_value_edit_callback
from fiatlight.fiat_kits.fiat_audio.audio_types import (
    SampleRate,
    SampleRatesExplained,
    NbChannels,
    NbChannelsExplained,
    BlockSize,
    BlockSizesExplained,
    SoundBlocksList,
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

    def _present_str(self, value: SoundBlocksList) -> str:
        return f"{len(value.blocks)} blocks at {value.sample_rate / 1000:.1f} kHz"


def register_audio_types_gui() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(SampleRate, SampleRateGui)
    register_type(NbChannels, NbChannelsGui)
    register_type(BlockSize, BlockSizeGui)
    register_type(SoundBlocksList, SoundBlocksListGui)


def sandbox() -> None:
    import fiatlight

    def my_function(sample_rate: SampleRate, nb_channels: NbChannels, block_size: BlockSize) -> None:
        pass

    fiatlight.fiat_run(my_function)


if __name__ == "__main__":
    sandbox()
