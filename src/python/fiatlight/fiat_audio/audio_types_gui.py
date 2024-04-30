"""Gui for simple types in fiat_audio.audio_types"""
from fiatlight.fiat_core import AnyDataWithGui, make_explained_value_edit_callback
from fiatlight.fiat_audio.audio_types import (
    SampleRate,
    SampleRatesExplained,
    NbChannels,
    NbChannelsExplained,
    BlockSize,
    BlockSizesExplained,
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
        self.callbacks.default_value_provider = lambda: BlockSize(512)
        self.callbacks.present_str = lambda x: f"{x} samples"


def register_audio_types_gui() -> None:
    from fiatlight.fiat_core import gui_factories

    prefix = "fiatlight.fiat_audio."
    gui_factories().register_factory(prefix + "audio_types.SampleRate", SampleRateGui)
    gui_factories().register_factory(prefix + "audio_types.NbChannels", NbChannelsGui)
    gui_factories().register_factory(prefix + "audio_types.BlockSize", BlockSizeGui)


def sandbox() -> None:
    import fiatlight

    def my_function(sample_rate: SampleRate, nb_channels: NbChannels, block_size: BlockSize) -> None:
        pass

    fiatlight.fiat_run(my_function)


if __name__ == "__main__":
    sandbox()
