"""AudioProvider interface for audio providers to implement.

- Users (player recorder, etc) should call get_sound_blocks() periodically to get the latest sound blocks.
  It returns a SoundBlocksList (i.e a list of sound blocks + sample rate) of yet unprocessed sound blocks.

- Derived classes should fill the queue by calling _enqueue_sound_block() with new sound blocks.

"""

from abc import ABC
from queue import Queue, Empty

from .audio_types import SoundBlocksList, SoundBlock, SoundStreamParams


class AudioProvider(ABC):
    _queue: Queue[SoundBlock]
    stream_params: SoundStreamParams

    def __init__(self, sound_stream_params: SoundStreamParams) -> None:
        self.stream_params = sound_stream_params
        self._queue = Queue()
        self._sd_stream = None

    def _enqueue_sound_block(self, block: SoundBlock) -> None:
        self._queue.put(block)

    def get_sound_blocks(self) -> SoundBlocksList:
        """Retrieves the latest blocks of audio data from the microphone, if available.
        Should be called repeatedly to get all available data.
        Ideally, you should call this quickly enough so that the list is either empty or contains only one block.
        Can be called from the main thread.
        """
        blocks = []
        try:
            while True:
                block = self._queue.get(block=False)
                blocks.append(block)
        except Empty:
            pass
        return SoundBlocksList(blocks, self.stream_params.sample_rate)
