"""SoundWave: a simple dataclass for storing audio waveforms, along with their sample rate."""
import numpy as np
import soundfile  # type: ignore

from fiatlight.fiat_array import FloatMatrix_Dim1
from fiatlight.fiat_types import AudioPath
from dataclasses import dataclass


@dataclass
class SoundWave:
    wave: FloatMatrix_Dim1
    sample_rate: int
    _time_array: FloatMatrix_Dim1 | None = None  # cache for time array

    def __post_init__(self) -> None:
        r = np.arange(0, self.duration(), 1 / self.sample_rate, self.wave.dtype)
        self._time_array = r  # type: ignore

    def duration(self) -> float:
        return len(self.wave) / self.sample_rate

    def nb_samples(self) -> int:
        return len(self.wave)

    def time_array(self) -> FloatMatrix_Dim1:
        assert self._time_array is not None
        return self._time_array

    def __str__(self) -> str:
        return f"{self.duration():.2f}s at {self.sample_rate / 1000:.1f} kHz"


def sound_wave_from_file(file_path: AudioPath) -> SoundWave:
    """Load a sound wave from a file."""
    wave, sample_rate = soundfile.read(file_path)
    # Convert to mono if necessary
    if wave.ndim == 2:
        wave = wave.mean(axis=1)
    return SoundWave(wave, sample_rate)
