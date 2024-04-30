from fiatlight.fiat_core import FunctionWithGui
from fiatlight.fiat_audio.microphone_io import MicrophoneParams, MicrophoneIo
from fiatlight.fiat_audio.audio_types import SoundBlock
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from fiatlight.fiat_audio.microphone_gui import MicrophoneParamsGui
from imgui_bundle import imgui, imgui_ctx, ImVec4, hello_imgui, ImVec2
from typing import List


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


def on_off_button_with_icons(is_on: bool, on_icon: str, off_icon: str) -> bool:
    icon = on_icon if is_on else off_icon
    # color: dark red if on, else dark gray
    color = ImVec4(1.0, 0.3, 0.3, 1.0) if is_on else ImVec4(0.7, 0.7, 0.7, 1.0)
    with imgui_ctx.push_style_color(imgui.Col_.text.value, color):
        with imgui_ctx.begin_horizontal("OnOffButton"):
            imgui.spring()
            button_size = hello_imgui.em_to_vec2(3, 3)
            clicked = imgui.button(icon, button_size)
            imgui.spring()
    return clicked


def microphone_on_off_button(is_on: bool) -> bool:
    return on_off_button_with_icons(
        is_on,
        icons_fontawesome_6.ICON_FA_MICROPHONE_LINES,
        icons_fontawesome_6.ICON_FA_MICROPHONE_LINES_SLASH,
    )


# class AudioProviderGui(FunctionWithGui):


class MicrophoneGui(FunctionWithGui):
    # Serialized options
    _microphone_params_gui: MicrophoneParamsGui

    # IO
    _microphone_io: MicrophoneIo

    # Live sound block plot
    _live_sound_block_plot_gui: _LiveSoundBlockPlotGui

    def __init__(self) -> None:
        # FunctionWithGui init
        super().__init__(self.f)
        self.name = "MicrophoneGui"
        # self.invoke_always_dirty = True
        self.internal_state_gui = self._internal_microphone_gui
        self.on_heartbeat = self._on_heartbeat

        # Initialize the live sound block plot
        self._live_sound_block_plot_gui = _LiveSoundBlockPlotGui()

        # Initialize the microphone
        self._microphone_params_gui = MicrophoneParamsGui()
        self._microphone_params_gui.value = MicrophoneParams()
        self._microphone_io = MicrophoneIo(self._microphone_params_gui.value)

    def f(self) -> int:
        return 1

    def _on_heartbeat(self) -> bool:
        sound_blocks = self._microphone_io.get_sound_blocks()
        self._live_sound_block_plot_gui.add_sound_blocks(sound_blocks)
        return False

    def _internal_microphone_gui(self) -> bool:
        """Draw the internal GUI of the function (mic related)"""
        with fontawesome_6_ctx():
            is_started = self._microphone_io.started()
            imgui.begin_disabled(is_started)
            _params_changed = self._microphone_params_gui.edit()
            imgui.end_disabled()
            if microphone_on_off_button(is_started):
                self._microphone_io.toggle()

        self._live_sound_block_plot_gui.gui()

        return False


def register_microphone_params_gui() -> None:
    from fiatlight.fiat_core import gui_factories

    prefix = "fiatlight.fiat_audio."
    gui_factories().register_factory(prefix + "microphone_io.MicrophoneParams", MicrophoneParamsGui)


def sandbox_microphone_params() -> None:
    import fiatlight

    def my_function(params: MicrophoneParams) -> None:
        pass

    register_microphone_params_gui()
    fiatlight.fiat_run(my_function)


def sandbox_microphone_gui() -> None:
    import fiatlight

    fn = MicrophoneGui()
    fiatlight.fiat_run(fn)


if __name__ == "__main__":
    # sandbox_microphone_params()
    sandbox_microphone_gui()
