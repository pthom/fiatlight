"""SoundWave: a simple dataclass for storing audio waveforms, along with their sample rate."""
import numpy as np
import soundfile  # type: ignore

from fiatlight.fiat_array import FloatMatrix_Dim1
from fiatlight.fiat_types import AudioPath, TimeSeconds
from dataclasses import dataclass
import scipy  # type: ignore
from typing import NewType
from numpy.typing import NDArray


# Possible sample rates for audio:
# 44100 Hz: This is the standard for audio CDs and is highly compatible across all playback systems. It's good for music and general audio recording.
# 48000 Hz: This is the standard for professional video production and streaming audio. It offers slightly higher fidelity and is common in film and TV production.
# 32000 Hz, 22050 Hz, and 16000 Hz: These are used for lower-fidelity applications, such as voice recording or telephony.
SampleRate = NewType("SampleRate", float)


# The number of samples in a block of sound data (typically 512 or 1024),
BlockSize = NewType("BlockSize", int)


# A live block of sound data, with shape (block_size, nb_channels),
# where block_size is the number of samples per channel, user-defined (typically 512 or 1024),
SoundBlock = NDArray[np.float32]


# The number of channels in a sound block (1 for mono, 2 for stereo, etc.)
NbChannels = NewType("NbChannels", int)


@dataclass
class SoundWave:
    wave: FloatMatrix_Dim1
    sample_rate: SampleRate
    _time_array: FloatMatrix_Dim1 | None = None  # cache for time array
    _max_intensity, _min_intensity = 1.0, -1.0

    def __post_init__(self) -> None:
        r = np.arange(0, self.duration(), 1 / self.sample_rate, self.wave.dtype)
        self._time_array = r  # type: ignore
        self._min_intensity = self.wave.min()
        self._max_intensity = self.wave.max()

    def duration(self) -> TimeSeconds:
        return len(self.wave) / self.sample_rate  # type: ignore

    def nb_samples(self) -> int:
        return len(self.wave)

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
