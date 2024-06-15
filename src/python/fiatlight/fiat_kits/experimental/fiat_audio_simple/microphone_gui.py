import numpy as np
from imgui_bundle import imgui, imgui_ctx, hello_imgui, ImVec2

from fiatlight.fiat_core import FunctionWithGui
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6, fiat_osd, misc_widgets

from .microphone_io import AudioProviderMic
from .audio_types import SoundBlock, SoundWave, SoundStreamParams
from fiatlight.fiat_togui.dataclass_gui import DataclassGui


class MicrophoneGui(FunctionWithGui):
    # Serialized options
    _microphone_params_gui: DataclassGui[SoundStreamParams]
    _sound_stream_params: SoundStreamParams
    _live_plot_size_em: ImVec2

    # IO
    _microphone_io: AudioProviderMic

    # Live sound blocks
    _displayed_sound_block: SoundBlock | None

    # Output being recorded
    _sound_wave_being_recorded: SoundBlock | None = None
    _is_recording: bool = False

    # Output after recording
    _sound_wave: SoundWave | None = None
    _was_recording_just_stopped: bool = False

    def __init__(self) -> None:
        super().__init__(self._f)
        self.function_name = "MicrophoneGui"
        self.internal_state_gui = self._internal_gui
        self.on_heartbeat = self._on_heartbeat

        self._microphone_params_gui = DataclassGui(SoundStreamParams)
        self._sound_stream_params = SoundStreamParams()
        self._microphone_io = AudioProviderMic()

        self._displayed_sound_block = None
        self._sound_wave_being_recorded = None
        self._live_plot_size_em = ImVec2(20, 10)

    def _f(self) -> SoundWave | None:
        return self._sound_wave

    def _clear(self) -> None:
        self._sound_wave = None
        self._sound_wave_being_recorded = None
        self._was_recording_just_stopped = False

    def _on_heartbeat(self) -> bool:
        sound_blocks = self._microphone_io.get_buffer().get_sound_blocks()

        # Display the last sound block
        if len(sound_blocks.blocks) > 0:
            self._displayed_sound_block = sound_blocks.blocks[-1]

        # Append sound blocks to the recording
        if self._is_recording:
            for sound_block in sound_blocks.blocks:
                if self._sound_wave_being_recorded is None:
                    self._sound_wave_being_recorded = sound_block
                else:
                    self._sound_wave_being_recorded = np.concatenate([self._sound_wave_being_recorded, sound_block])

        # Trigger a call to self._f() if the recording was just stopped
        needs_refresh = self._was_recording_just_stopped
        self._was_recording_just_stopped = False
        return needs_refresh

    def _on_start_recording(self) -> None:
        self._microphone_io.start(self._sound_stream_params)
        self._sound_wave = None
        self._is_recording = True

    def _on_stop_recording(self) -> None:
        self._microphone_io.stop()
        self._sound_wave = SoundWave(self._sound_wave_being_recorded, self._sound_stream_params.sample_rate)  # type: ignore
        self._was_recording_just_stopped = True
        self._is_recording = False

    def _show_live_sound_block(self) -> None:
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
                implot.setup_axes_limits(0, len(block), -1, 1)
                implot.plot_line("##SoundBlock", block)

            self._live_plot_size_em = show_resizable_plot_in_node_editor_em(
                "SoundBlock", self._live_plot_size_em, plot_fn
            )

    def _draw_microphone_button(self) -> None:
        is_started = self._microphone_io.started()

        clicked = misc_widgets.on_off_button(
            "##on_off_mic",
            is_started,
            icons_fontawesome_6.ICON_FA_MICROPHONE_LINES_SLASH,
            icons_fontawesome_6.ICON_FA_MICROPHONE_LINES,
            "Start recording",
            "Stop recording",
        )

        if clicked:
            if is_started:
                self._on_stop_recording()
            else:
                self._on_start_recording()

    def _draw_control_buttons(self) -> bool:
        changed = False
        with imgui_ctx.begin_horizontal("ControlButtons"):
            self._draw_microphone_button()
            if self._sound_wave is not None:
                button_size = hello_imgui.em_to_vec2(3, 3)
                if imgui.button(icons_fontawesome_6.ICON_FA_TRASH, button_size):
                    self._clear()
                    changed = True
                fiat_osd.set_widget_tooltip("Delete the recorded sound wave")
        return changed

    def _internal_gui(self) -> bool:
        """Draw the internal GUI of the function."""
        with fontawesome_6_ctx():
            is_started = self._microphone_io.started()
            has_data = self._sound_wave is not None or self._sound_wave_being_recorded is not None

            imgui.begin_disabled(is_started or has_data)
            _params_changed = self._microphone_params_gui.edit(self._sound_stream_params)
            imgui.end_disabled()
            need_refresh = self._draw_control_buttons()
            self._show_live_sound_block()

        return need_refresh
