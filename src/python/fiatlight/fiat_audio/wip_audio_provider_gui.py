from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_audio.audio_types import SoundBlock
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_audio.wip_audio_provider import AudioProvider
from imgui_bundle import ImVec2, imgui, imgui_ctx
from typing import List, Any
from abc import ABC, abstractmethod


class _LiveSoundBlockPlotGui:
    # Live sound blocks
    _displayed_sound_block: SoundBlock | None

    # serializable option
    _live_plot_size_em: ImVec2

    def __init__(self) -> None:
        self._displayed_sound_block = None
        self._live_plot_size_em = ImVec2(20, 10)

    def add_sound_blocks(self, sound_blocks: List[SoundBlock]) -> None:
        if len(sound_blocks) > 0:
            self._displayed_sound_block = sound_blocks[-1]

    def gui(self) -> None:
        block = self._displayed_sound_block
        if block is None:
            return
        with imgui_ctx.begin_vertical("LiveSoundBlock"):
            max_intensity = block.max()
            avg_intensity = block.mean()
            nb_channels = len(block.shape)
            imgui.text(f"Max: {max_intensity:.2f}, Avg: {avg_intensity:.2f}, Channels: {nb_channels}")

            from imgui_bundle import implot
            from imgui_bundle.immapp import show_resizable_plot_in_node_editor_em

            def plot_fn() -> None:
                implot.setup_axes_limits(0, len(block), -1, 1, imgui.Cond_.always.value)
                implot.plot_line("##SoundBlock", block)

            self._live_plot_size_em = show_resizable_plot_in_node_editor_em(
                "SoundBlock", self._live_plot_size_em, plot_fn
            )


class AudioProviderGui(FunctionWithGui, ABC):
    _audio_provider: AudioProvider
    # Live sound block plot
    _live_sound_block_plot_gui: _LiveSoundBlockPlotGui
    # Available sound blocks
    _sound_blocks: List[SoundBlock]

    def __init__(self, audio_provider: AudioProvider) -> None:
        self._audio_provider = audio_provider
        # FunctionWithGui init
        super().__init__(self.f)
        self.internal_state_gui = self._internal_gui
        self.on_heartbeat = self._on_heartbeat
        self.invoke_always_dirty = True

        self._sound_blocks = []

        # Initialize the live sound block plot
        self._live_sound_block_plot_gui = _LiveSoundBlockPlotGui()

        # Add output GUI
        output_gui_undef = AnyDataWithGui[Any]()
        self.add_output(output_gui_undef)

    def f(self) -> List[SoundBlock]:
        return self.sound_blocks

    def _on_heartbeat(self) -> bool:
        self.sound_blocks = self._audio_provider.get_sound_blocks()
        self._live_sound_block_plot_gui.add_sound_blocks(self.sound_blocks)
        return False

    def _internal_gui(self) -> bool:
        needs_refresh = self.specialized_internal_gui()
        self._live_sound_block_plot_gui.gui()
        return needs_refresh

    @abstractmethod
    def specialized_internal_gui(self) -> bool:
        pass
