"""SoundWaveGui class for displaying SoundWave data in a GUI."""
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.demos.audio.sound_wave import SoundWave
from fiatlight.demos.audio import audio_functions
from imgui_bundle import implot, imgui, hello_imgui


class SoundWaveGui(AnyDataWithGui[SoundWave]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.present_custom = self.present_custom

    def present_custom(self) -> None:
        sound_wave = self.get_actual_value()
        imgui.text(f"Duration: {sound_wave.duration():.2f} s, Sample Rate: {sound_wave.sample_rate} Hz")
        plot_size = hello_imgui.em_to_vec2(20, 10)
        if implot.begin_plot("##Audio Waveform", plot_size):
            implot.setup_axes(
                "Time [s]", "Amplitude", implot.AxisFlags_.auto_fit.value, implot.AxisFlags_.auto_fit.value
            )
            # implot.plot_line("Waveform", sound_wave.time_array(), sound_wave.wave)
            implot.plot_line("Waveform", sound_wave.time_array(), sound_wave.wave)
            implot.end_plot()

        if imgui.button("Play"):
            audio_functions.play_audio(sound_wave)
