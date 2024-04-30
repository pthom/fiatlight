from fiatlight.fiat_audio.microphone_io import MicrophoneParams, MicrophoneIo
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from fiatlight.fiat_audio.microphone_gui import MicrophoneParamsGui
from fiatlight.fiat_audio.wip_audio_provider_gui import AudioProviderGui
from imgui_bundle import imgui, imgui_ctx, ImVec4, hello_imgui


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


class MicrophoneGui(AudioProviderGui):
    # Serialized options
    _microphone_params_gui: MicrophoneParamsGui
    # IO
    _microphone_io: MicrophoneIo

    def __init__(self) -> None:
        # Initialize the microphone
        self._microphone_params_gui = MicrophoneParamsGui()
        self._microphone_params_gui.value = MicrophoneParams()
        self._microphone_io = MicrophoneIo(self._microphone_params_gui.value)

        # FunctionWithGui init
        super().__init__(self._microphone_io)
        self.name = "MicrophoneGui"

    def specialized_internal_gui(self) -> bool:
        """Draw the internal GUI of the function (mic related)"""
        with fontawesome_6_ctx():
            is_started = self._microphone_io.started()
            imgui.begin_disabled(is_started)
            _params_changed = self._microphone_params_gui.edit()
            imgui.end_disabled()
            if microphone_on_off_button(is_started):
                self._microphone_io.toggle()

        return False


def sandbox_microphone_gui() -> None:
    import fiatlight

    fn = MicrophoneGui()
    fiatlight.fiat_run(fn)


if __name__ == "__main__":
    sandbox_microphone_gui()
