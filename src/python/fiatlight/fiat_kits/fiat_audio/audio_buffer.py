"""AudioBuffer: a thread-safe buffer for sound blocks.

- Consumers should call get_sound_blocks() periodically to get the latest sound blocks.
  It returns a SoundBlocksList (i.e a list of sound blocks + sample rate) of yet unprocessed sound blocks.

- Providers should fill the queue by calling _enqueue_sound_block() with new sound blocks.

"""

from queue import Queue, Empty

from .sound_wave import SoundWave, concatenate_sound_waves


class AudioBuffer:
    _queue: Queue[SoundWave]

    def __init__(self) -> None:
        self._queue = Queue()

    def enqueue(self, sound_wave: SoundWave) -> None:
        self._queue.put(sound_wave)

    def has_data(self) -> bool:
        """Returns True if there is sound available in the queue."""
        return not self._queue.empty()

    def get(self) -> SoundWave:
        """Retrieves the latest blocks of audio data from the microphone, if available.
        Should be called repeatedly to get all available data.
        Ideally, you should call this quickly enough so that the queue is periodically emptied.
        Can be called from the main thread.
        """
        sound_waves = []
        try:
            while True:
                sound_wave = self._queue.get(block=False)
                sound_waves.append(sound_wave)
        except Empty:
            pass

        if len(sound_waves) == 0:
            return SoundWave.make_empty()

        # Check that all sound waves have the same sample rate
        sample_rate = sound_waves[0].sample_rate
        for sound_wave in sound_waves:
            if sound_wave.sample_rate != sample_rate:
                raise ValueError("All sound waves in the queue should have the same sample rate")

        # Concatenate all sound waves
        wave = concatenate_sound_waves(sound_waves)
        return wave
