"""SoundWave: a simple dataclass for storing audio waveforms, along with their sample rate."""

import numpy as np
import soundfile  # type: ignore

from fiatlight.fiat_types import AudioPath, TimeSeconds
from fiatlight.fiat_utils import add_fiat_attributes
from numpy.typing import NDArray
from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass


SampleRate = int
BlockSize = int


# A live block of sound data, with shape (block_size, nb_channels),
# where block_size is the number of samples per channel, user-defined (typically 512 or 1024),
# ShapeDim1 = tuple[int]
# ShapeDim2 = tuple[int, int]
# SoundBlock = NewType("SoundBlock", np.ndarray[ShapeDim1 | ShapeDim2, np.dtype[np.float32]])
# SoundData = NewType("SoundData", np.ndarray[ShapeDim1 | ShapeDim2, np.dtype[np.float32]])
SoundBlock = NDArray[np.float32]
SoundData = NDArray[np.float32]


class SampleRatesCommon(Enum):
    """Common sample rates for sound data."""

    Hz8000 = 8000  # 8kHz: telephone quality
    Hz22050 = 22050  # 22.05kHz: FM radio quality
    Hz32000 = 32000  # 32kHz
    Hz44100 = 44100  # 44.1kHz: CD quality
    Hz48000 = 48000  # 48kHz: DVD quality


add_fiat_attributes(
    SampleRatesCommon,
    Hz8000__label="8kHz",
    Hz8000__tooltip="Telephone quality",
    Hz22050__label="22.05kHz",
    Hz22050__tooltip="FM radio quality",
    Hz32000__label="32kHz",
    Hz44100__label="44.1kHz",
    Hz44100__tooltip="CD quality",
    Hz48000__label="48kHz",
    Hz48000__tooltip="DVD quality",
)


class BlockSizesCommon(Enum):
    """Common block sizes for sound data."""

    Size256 = 256
    Size512 = 512
    Size1024 = 1024


add_fiat_attributes(BlockSizesCommon, use_value_as_label=True)


class SoundRecordParams(BaseModel):
    """A *small* subset of parameters for a sound stream
    (available in the sounddevice library)
    This simple audio library only supports mono sound.
    """

    sample_rate: SampleRatesCommon = SampleRatesCommon.Hz44100
    block_size: BlockSizesCommon = BlockSizesCommon.Size512


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
        return f"{len(self.blocks)} blocks at {self.sample_rate / 1000:.1f} kHz"


@dataclass
class SoundWave:
    wave: SoundData
    sample_rate: SampleRate

    @staticmethod
    def make_empty() -> "SoundWave":
        empty_wave = np.zeros((1,), np.float32)
        return SoundWave(empty_wave, SampleRate(44100))

    def duration(self) -> TimeSeconds:
        return TimeSeconds(len(self.wave) / self.sample_rate)

    def nb_samples(self) -> int:
        return len(self.wave)

    def nb_channels(self) -> int:
        if len(self.wave.shape) == 1:
            return 1
        return self.wave.shape[1]

    def is_empty(self) -> bool:
        return self.wave.size == 0

    def __str__(self) -> str:
        return f"{self.duration():.2f}s, {self.nb_channels()} chan,  {self.sample_rate / 1000:.1f} kHz"


def sound_wave_from_file(file_path: AudioPath) -> SoundWave:
    """Load a sound wave from a file."""
    wave, sample_rate = soundfile.read(file_path, dtype="float32")
    return SoundWave(wave, sample_rate)


def extract_flattened_channel(wave: SoundData, channel: int) -> SoundData:
    if len(wave.shape) == 1:
        return wave
    nb_channels = wave.shape[1]
    assert 0 <= channel < nb_channels
    return wave[:, channel].flatten()
