from fiatlight.fiat_audio.audio_types import SoundBlocksList
from abc import ABC, abstractmethod


class AudioProvider(ABC):
    @abstractmethod
    def get_sound_blocks(self) -> SoundBlocksList:
        pass
