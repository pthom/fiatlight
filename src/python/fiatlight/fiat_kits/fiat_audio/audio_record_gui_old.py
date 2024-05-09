"""AudioRecordGui: a FunctionWithGui that outputs audio, and can record audio from the microphone
"""
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_kits.fiat_audio.audio_types import SoundWave, SampleRate
from fiatlight.fiat_kits.fiat_audio import audio_functions
from imgui_bundle import imgui, hello_imgui

from dataclasses import dataclass


@dataclass
class AudioRecordParams:
    duration: float = 5.0
    sample_rate: SampleRate = 44100  # type: ignore

    def __str__(self) -> str:
        return f"{self.duration}s, Rate: {self.sample_rate}"


class AudioRecordParamsGui(AnyDataWithGui[AudioRecordParams]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: AudioRecordParams()

    def edit(self) -> bool:
        audio_params = self.get_actual_value()
        imgui.set_next_item_width(hello_imgui.em_size(10))
        changed1, audio_params.duration = imgui.slider_float("Duration", audio_params.duration, 0.1, 100.0)
        imgui.set_next_item_width(hello_imgui.em_size(10))
        changed2, audio_params.sample_rate = imgui.slider_float("Sample Rate", audio_params.sample_rate, 8000, 96000)  # type: ignore
        return changed1 or changed2


class AudioRecordGui(FunctionWithGui):
    def __init__(self) -> None:
        super().__init__(self._record_audio)
        self.name = "AudioRecordGui"
        # This function should be called manually by the user
        self.set_invoke_manually_io()
        # And it should be called asynchronously, to avoid blocking the UI
        self.set_invoke_async()

        self.param("params").data_with_gui = AudioRecordParamsGui()

    def _record_audio(self, params: AudioRecordParams) -> SoundWave:
        """Record audio from the microphone for a given duration and sample rate."""
        r = audio_functions.record_audio(params.duration, params.sample_rate)
        return r
