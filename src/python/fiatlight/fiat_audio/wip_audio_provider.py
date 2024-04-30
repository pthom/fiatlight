from fiatlight.fiat_audio.audio_types import SoundBlock
from typing import List
from abc import ABC, abstractmethod


class AudioProvider(ABC):
    @abstractmethod
    def get_sound_blocks(self) -> List[SoundBlock]:
        pass
