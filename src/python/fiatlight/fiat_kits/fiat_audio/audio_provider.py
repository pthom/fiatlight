"""AudioProvider: interface for audio providers to implement.

- Users (player recorder, etc) should call get_sound_blocks() periodically to get the latest sound blocks.
  It returns a SoundBlocksList (i.e a list of sound blocks + sample rate) of yet unprocessed sound blocks.

- Derived classes or providers should fill the queue by calling _enqueue_sound_block() with new sound blocks.

"""

from queue import Queue, Empty

from .audio_types import SoundBlocksList, SoundBlock, SampleRate


class AudioProvider:
    _queue: Queue[SoundBlock]
    _sample_rate: SampleRate = SampleRate(0)

    def __init__(self) -> None:
        self._queue = Queue()
        self._sd_stream = None

    def _enqueue_sound_block(self, block: SoundBlock, sample_rate: SampleRate) -> None:
        if not self._queue.empty():
            # Ensure that all blocks have the same sample rate
            if sample_rate != self._sample_rate:
                raise ValueError("All sound blocks must have the same sample rate")
        else:
            self._sample_rate = sample_rate
        self._queue.put(block)

    def has_sound_blocks(self) -> bool:
        """Returns True if there are sound blocks available in the queue."""
        return not self._queue.empty()

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
        return SoundBlocksList(blocks, self._sample_rate)
