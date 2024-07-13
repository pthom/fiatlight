"""SoundWave: a simple dataclass for storing audio waveforms, along with their sample rate."""

import numpy as np
import soundfile  # type: ignore

from fiatlight.fiat_kits.fiat_implot import FloatMatrix_Dim1
from fiatlight.fiat_types import AudioPath, TimeSeconds
from numpy.typing import NDArray
import scipy  # type: ignore
from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass


# A live block of sound data, with shape (block_size, nb_channels),
# where block_size is the number of samples per channel, user-defined (typically 512 or 1024),
SoundBlock = NDArray[np.float32]


class SampleRate(Enum):
    """Common sample rates for sound data."""
    Hz8000 = 8000
    Hz22050 = 22050
    Hz32000 = 32000
    Hz44100 = 44100
    Hz48000 = 48000


class BlockSize(Enum):
    """Common block sizes for sound data."""
    Size256 = 256
    Size512 = 512
    Size1024 = 1024


class SoundStreamParams(BaseModel):
    """A *small* subset of parameters for a sound stream
    (available in the sounddevice library)
    This simple audio library only supports mono sound.
    """

    sample_rate: SampleRate = SampleRate.Hz44100
    block_size: BlockSize = BlockSize.Size512


@dataclass
class SoundBlocksList:
    blocks: list[SoundBlock]
    sample_rate: SampleRate

    @staticmethod
    def make_empty() -> "SoundBlocksList":
        return SoundBlocksList([], SampleRate(44100))

    def is_empty(self) -> bool:
        return len(self.blocks) == 0

    def __str__(self) -> str:
        return f"{len(self.blocks)} blocks at {self.sample_rate.value / 1000:.1f} kHz"



@dataclass
class SoundWave:
    wave: FloatMatrix_Dim1
    sample_rate: SampleRate
    _time_array: FloatMatrix_Dim1 | None = None  # cache for time array
    _max_intensity, _min_intensity = 1.0, -1.0

    def __post_init__(self) -> None:
        if self.is_empty():
            return

        # SoundWave only supports mono
        if self.wave.ndim == 2 and self.wave.shape[1] > 1:
            self.wave = self.wave.mean(axis=0)
            # remove the second dimension
            self.wave = self.wave.squeeze()  # type: ignore

        time_array = np.arange(0, self.duration(), 1 / self.sample_rate.value, self.wave.dtype)
        self._time_array = time_array  # type: ignore
        self._min_intensity = self.wave.min()
        self._max_intensity = self.wave.max()

    @staticmethod
    def make_empty() -> "SoundWave":
        empty_wave: FloatMatrix_Dim1 = np.array([], dtype=np.float32)  # type: ignore
        return SoundWave(empty_wave, SampleRate(44100))

    def duration(self) -> TimeSeconds:
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
        new_sample_rate = SampleRate(self.sample_rate.value * num_samples / len(self.wave))
        return SoundWave(wave_resampled, new_sample_rate)

    def time_array(self) -> FloatMatrix_Dim1:
        assert self._time_array is not None
        return self._time_array  # noqa

    def __str__(self) -> str:
        return f"{self.duration():.2f}s at {self.sample_rate.value / 1000:.1f} kHz"


def sound_wave_from_file(file_path: AudioPath) -> SoundWave:
    """Load a sound wave from a file."""
    wave, sample_rate = soundfile.read(file_path)
    # Convert to mono if necessary
    if wave.ndim == 2:
        wave = wave.mean(axis=1)
    return SoundWave(wave, sample_rate)
