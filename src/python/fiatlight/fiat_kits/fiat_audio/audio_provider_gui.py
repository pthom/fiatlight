"""AudioProviderGui: a GUI wrapper for an AudioProvider.

It displays the live sound blocks.
It may be derived and specialized by overriding the specialized_internal_gui() method.
"""
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from imgui_bundle import ImVec2, imgui, imgui_ctx
from typing import List
from abc import ABC

from .audio_types import SoundBlocksList, SoundBlock
from .audio_provider import AudioProvider


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
    _sound_blocks_list: SoundBlocksList

    def __init__(self, audio_provider: AudioProvider) -> None:
        self._audio_provider = audio_provider

        # FunctionWithGui init
        super().__init__(self.f)
        self.internal_state_gui = self._internal_gui
        self.on_heartbeat = self._on_heartbeat
        # self.invoke_always_dirty = True

        # Initialize the sound block list and its plot
        self._sound_blocks_list = SoundBlocksList.make_empty()
        self._live_sound_block_plot_gui = _LiveSoundBlockPlotGui()

    def specialized_internal_gui(self) -> bool:
        return False

    def f(self) -> SoundBlocksList:
        return self._sound_blocks_list

    def _on_heartbeat(self) -> bool:
        self._sound_blocks_list = self._audio_provider.get_sound_blocks()
        self._live_sound_block_plot_gui.add_sound_blocks(self._sound_blocks_list.blocks)
        has_new_blocks = len(self._sound_blocks_list.blocks) > 0
        return has_new_blocks

    def _internal_gui(self) -> bool:
        # Display the specialized internal GUI (for derived classes: for example, the microphone On/Off button)
        changed = self.specialized_internal_gui()

        # Display the live sound block plot
        self._live_sound_block_plot_gui.gui()

        return changed
