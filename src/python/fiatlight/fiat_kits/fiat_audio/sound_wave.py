from dataclasses import dataclass
import numpy as np
import scipy  # type: ignore

from fiatlight.fiat_types import TimeSeconds, AudioPath
from .audio_types import SoundData
from fiatlight.fiat_kits.fiat_array import FloatMatrix_Dim1
from .audio_types import SampleRate


@dataclass
class SoundWave:
    wave: SoundData
    sample_rate: SampleRate
    _time_array: FloatMatrix_Dim1 | None = None  # cache for time array
    _max_intensity, _min_intensity = 1.0, -1.0

    def __post_init__(self) -> None:
        if self.is_empty():
            return
        assert self.sample_rate > 0
        time_array = np.arange(0, self.duration(), 1 / self.sample_rate, self.wave.dtype)
        self._time_array = time_array  # type: ignore
        self._min_intensity = self.wave.min()
        self._max_intensity = self.wave.max()

    @staticmethod
    def make_empty() -> "SoundWave":
        empty_wave: FloatMatrix_Dim1 = np.array([], dtype=np.float32)  # type: ignore
        return SoundWave(empty_wave, SampleRate(44100))

    def duration(self) -> TimeSeconds:
        if self.is_empty():
            return TimeSeconds(0)
        return len(self.wave) / self.sample_rate  # type: ignore

    def nb_samples(self) -> int:
        return len(self.wave)

    def is_empty(self) -> bool:
        return self.wave.size == 0

    def _rough_resample_to_max_samples(self, max_samples: int) -> "SoundWave":
        """Resample the sound wave to have at most max_samples.
        Do not trust this for sound. This is only used for plotting, for performance reasons.
        """
        if len(self.wave) <= max_samples:
            return self

        num_samples = max_samples
        wave_resampled = scipy.signal.resample(self.wave, max_samples)
        new_sample_rate = SampleRate(self.sample_rate * num_samples / len(self.wave))
        return SoundWave(wave_resampled, new_sample_rate)

    def time_array(self) -> FloatMatrix_Dim1:
        assert self._time_array is not None
        return self._time_array  # noqa

    def __str__(self) -> str:
        return f"{self.duration():.2f}s at {self.sample_rate / 1000:.1f} kHz"


def sound_wave_from_file(file_path: AudioPath) -> SoundWave:
    """Load a sound wave from a file."""
    import soundfile  # type: ignore

    wave, sample_rate = soundfile.read(file_path)
    # Convert to mono if necessary
    if wave.ndim == 2:
        wave = wave.mean(axis=1)
    return SoundWave(wave, sample_rate)


def concatenate_sound_waves(waves: list[SoundWave]) -> SoundWave:
    """Concatenate a list of sound waves."""
    if len(waves) == 0:
        return SoundWave.make_empty()
    wave = np.concatenate([w.wave for w in waves])
    sample_rate = waves[0].sample_rate

    # Check that all waves have the same sample rate
    for w in waves[1:]:
        if w.sample_rate != sample_rate:
            raise ValueError("All sound waves must have the same sample rate to be concatenated.")

    return SoundWave(wave, sample_rate)
