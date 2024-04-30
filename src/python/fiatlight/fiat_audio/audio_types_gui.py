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
        self.callbacks.default_value_provider = lambda: BlockSize(1024)
        self.callbacks.present_str = lambda x: f"{x} samples"


# class SoundBlockGui(AnyDataWithGui[SoundBlock]):
#     def __init__(self) -> None:
#         super().__init__()
#         self.callbacks.present_str = self._present_str
#         self.callbacks.present_custom = self._present_custom
#
#     def _present_str(self, value: SoundBlock) -> str:
#         # Example: Mono, 512 samples, max=0.5, avg=0.1
#         if len(value.shape) == 0:
#             return "Empty sound block"
#         max_intensity = value.max()
#         avg_intensity = value.mean()
#         nb_channels = len(value.shape)
#         return f"TBC"
#
#     def _present_custom(self) -> None:
#         sound_block = self.get_actual_value()
#         if len(sound_block.shape) == 0:
#             return
#         # Plot the sound block
#         from imgui_bundle import implot
#         from imgui_bundle.immapp import show_resizable_plot_in_node_editor_em
#         plot_size_em = ImVec2(20, 10)
#
#         def plot_fn() -> None:
#             implot.setup_axes_limits(0, len(sound_block), -1, 1)
#             implot.plot_line("##SoundBlock", sound_block)
#
#         show_resizable_plot_in_node_editor_em("SoundBlock", plot_size_em, plot_fn)


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
