import fiatlight as fl
from pydantic import BaseModel
from fiatlight.fiat_togui.basemodel_gui import BaseModelGui
from fiatlight.fiat_kits.experimental.fiat_audio_simple import SoundWave, sound_wave_from_file
from imgui_bundle import imgui, hello_imgui
import numpy as np


class SoundTransformParams(BaseModel):
    """
    Parameters for transforming audio playback.
    - `pitch_semitones`: change in pitch, in semitones (-12 to +12 typical range)
    - `tempo_percent`: playback speed as a percentage of original tempo
    """

    pitch_semitones: float = 0.0
    tempo_ratio: float = 1.0

    def is_default(self) -> bool:
        import math

        return math.fabs(self.pitch_semitones) < 0.01 and math.fabs(self.tempo_ratio - 1.0) < 0.01


def apply_sound_transform_pedalboard(
    wave: SoundWave,
    sound_transform: SoundTransformParams | None = None,
) -> SoundWave:
    from pedalboard import time_stretch  # type: ignore
    import numpy as np

    if (
        sound_transform is None
        or wave.is_empty()
        or (sound_transform.tempo_ratio == 1.0 and sound_transform.pitch_semitones == 0.0)
    ):
        return wave

    audio = wave.wave.astype(np.float32)

    processed = time_stretch(
        audio,
        samplerate=float(wave.sample_rate),
        stretch_factor=sound_transform.tempo_ratio,
        pitch_shift_in_semitones=sound_transform.pitch_semitones,
        high_quality=True,
    )

    return SoundWave(processed.astype(np.float32), wave.sample_rate)


def apply_sound_transform_librosa(wave: SoundWave, sound_transform: SoundTransformParams | None = None) -> SoundWave:
    import librosa

    if sound_transform is None or wave.is_empty() or sound_transform.is_default():
        return wave

    y = wave.wave.T  # librosa expects shape (n_channels, n_samples)
    if y.ndim == 1:
        y = y[np.newaxis, :]  # shape: (1, n_samples)

    processed_channels = []
    for ch in y:
        y_tempo = librosa.effects.time_stretch(ch, rate=sound_transform.tempo_ratio)
        y_pitch = librosa.effects.pitch_shift(y_tempo, sr=wave.sample_rate, n_steps=sound_transform.pitch_semitones)
        processed_channels.append(y_pitch)

    # Stack back and transpose to (n_samples, n_channels) if multichannel
    transformed_wave = np.stack(processed_channels, axis=0).T.astype(np.float32)

    return SoundWave(transformed_wave, wave.sample_rate)


def apply_sound_transform(wave: SoundWave, sound_transform: SoundTransformParams | None = None) -> SoundWave:
    """Apply pitch and tempo transformations to a sound wave.
    This is slow, so you have to invoke it manually.
    """
    # pedalboard is twice slower than librosa in this case!
    return apply_sound_transform_librosa(wave, sound_transform)
    # return apply_sound_transform_pedalboard(wave, sound_transform)


class SoundTransformParamsGui(BaseModelGui[SoundTransformParams]):
    def __init__(self) -> None:
        super().__init__(SoundTransformParams)
        self.callbacks.edit = self.edit

    def edit(self, param: SoundTransformParams) -> tuple[bool, SoundTransformParams]:
        changed = False

        imgui.set_next_item_width(hello_imgui.em_size(10))
        edited, param.pitch_semitones = imgui.input_float(
            "Pitch Semitones", param.pitch_semitones, step=0.1, step_fast=1.0
        )
        changed |= edited

        imgui.set_next_item_width(hello_imgui.em_size(10))
        edited, param.tempo_ratio = imgui.input_float("Tempo Ratio", param.tempo_ratio, step=0.01, step_fast=0.1)
        changed |= edited

        if imgui.button("Reset"):
            param.pitch_semitones = 0.0
            param.tempo_ratio = 1.0
            changed = True

        return changed, param


fl.register_type(SoundTransformParams, SoundTransformParamsGui)
fl.add_fiat_attributes(apply_sound_transform, invoke_async=True, invoke_manually=True)

graph = fl.FunctionsGraph.from_function_composition([sound_wave_from_file, apply_sound_transform])
graph.add_markdown_node(
    """
A simple singing practice tool, where you can load a sound file and apply pitch and tempo transformations.
You can also set markers to indicate the start of a section you want to practice.
"""
)
fl.run(graph, app_name="sing_practice")
