"""SoundWave: a simple dataclass for storing audio waveforms, along with their sample rate."""

from fiatlight.fiat_types import ExplainedValue, ExplainedValues
from typing import NewType
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass


# Possible sample rates for audio (typically 8000, 22050, 44100, 48000),
SampleRate = NewType("SampleRate", float)

# The number of channels in a sound block (1 for mono, 2 for stereo, etc.)
NbChannels = NewType("NbChannels", int)

# The number of samples in a block of sound data (typically 512 or 1024),
BlockSize = NewType("BlockSize", int)

# A block of sound data, with shape (nb_samples, nb_channels),
SoundData = NDArray[np.float32]

# A live block of sound data, with shape (block_size, nb_channels),
# where block_size is the number of samples per channel, user-defined (typically 512 or 1024),
# (used when communicating with sounddevice)
SoundBlock = NDArray[np.float32]


@dataclass
class SoundStreamParams:
    """A *small* subset of parameters for a sound stream
    (available in the sounddevice library)"""

    sample_rate: SampleRate = SampleRate(44100)
    nb_channels: NbChannels = NbChannels(1)
    block_size: BlockSize = BlockSize(512)


#  --------------------------------------------------------------------------------------------
#         Gui Hints for those types
#  --------------------------------------------------------------------------------------------
SampleRatesExplained: ExplainedValues[SampleRate] = [
    ExplainedValue(SampleRate(8000), "8Khz", "Analog telephone"),
    ExplainedValue(SampleRate(22050), "22kHz", "22050Hz, low quality"),
    ExplainedValue(SampleRate(32000), "32kHz", "32000Hz"),
    ExplainedValue(SampleRate(44100), "44kHz", "44100Hz, CD quality"),
    ExplainedValue(SampleRate(48000), "48kHz", "48000Hz, production quality"),
]


BlockSizesExplained: ExplainedValues[BlockSize] = [
    ExplainedValue(BlockSize(256), "256", "Small block size"),
    ExplainedValue(BlockSize(512), "512", "Standard"),
    ExplainedValue(BlockSize(1024), "1024", "Large block size"),
]


NbChannelsExplained: ExplainedValues[NbChannels] = [
    ExplainedValue(NbChannels(1), "Mono", "1 channel"),
    ExplainedValue(NbChannels(2), "Stereo", "2 channels"),
]
