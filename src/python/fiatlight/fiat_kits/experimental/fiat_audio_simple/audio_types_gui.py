"""Gui for simple types in fiat_audio.audio_types"""
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_togui import make_explained_value_edit_callback
from .audio_types import (
    SampleRate,
    SampleRatesExplained,
    BlockSize,
    BlockSizesExplained,
    SoundBlocksList,
)


class SampleRateGui(AnyDataWithGui[SampleRate]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = make_explained_value_edit_callback("sample_rate", SampleRatesExplained)
        self.callbacks.default_value_provider = lambda: SampleRate(44100)
        self.callbacks.present_str = lambda x: f"{x / 1000} kHz"


class BlockSizeGui(AnyDataWithGui[BlockSize]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = make_explained_value_edit_callback("block_size", BlockSizesExplained)
        self.callbacks.default_value_provider = lambda: BlockSize(1024)
        self.callbacks.present_str = lambda x: f"{x} samples"


class SoundBlocksListGui(AnyDataWithGui[SoundBlocksList]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.present_str = self._present_str

    @staticmethod
    def _present_str(value: SoundBlocksList) -> str:
        return f"{len(value.blocks)} blocks at {value.sample_rate / 1000:.1f} kHz"


def register_audio_types_gui() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(SampleRate, SampleRateGui)
    register_type(BlockSize, BlockSizeGui)
    register_type(SoundBlocksList, SoundBlocksListGui)
