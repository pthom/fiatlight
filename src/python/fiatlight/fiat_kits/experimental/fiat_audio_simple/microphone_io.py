import sounddevice as sd  # type: ignore
from typing import Any, Optional
import logging
from queue import Queue, Empty
from .audio_types import SoundBlock, SoundRecordParams, SoundBlocksList, SampleRate


class MicrophoneBuffer:
    """Thread-safe buffer for audio data. Used to pass audio data from the microphone to the main thread."""

    _queue: Queue[SoundBlock]
    _sample_rate: SampleRate = SampleRate(44100)

    def __init__(self) -> None:
        self._queue = Queue()

    def enqueue_sound_block(self, block: SoundBlock, sample_rate: SampleRate) -> None:
        # logging.warning(f"Enqueueing sound block: {block.shape}")
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
        Ideally, you should call this quickly enough so that the list contains only few blocks.
        Can be called from the main thread.
        """
        blocks = []
        try:
            while True:
                block = self._queue.get(block=False)
                blocks.append(block)
        except Empty:
            pass

        if len(blocks) > 0 and self._sample_rate <= 0:  # noqa
            raise ValueError("Sample rate not set")
        return SoundBlocksList(blocks, self._sample_rate)


class AudioProviderMic:
    _sd_stream: Optional[sd.InputStream]
    _audio_buffer: MicrophoneBuffer

    def __init__(self) -> None:
        super().__init__()
        self._audio_buffer = MicrophoneBuffer()
        self._sd_stream = None

    def start(self, stream_params: SoundRecordParams) -> None:
        """Manually start the microphone input, when not using the context manager."""
        self._start_io(stream_params)

    def stop(self) -> None:
        """Manually stop the microphone input, when not using the context manager."""
        self._stop_io()

    def toggle(self, stream_params: SoundRecordParams) -> None:
        """Toggle the microphone input on/off."""
        if self.started():
            self.stop()
        else:
            self.start(stream_params)

    def started(self) -> bool:
        """Check if the microphone input is currently running."""
        return self._sd_stream is not None

    def get_buffer(self) -> MicrophoneBuffer:
        return self._audio_buffer

    def _start_io(self, stream_params: SoundRecordParams) -> None:
        try:
            self._sd_stream = sd.InputStream(
                samplerate=int(stream_params.sample_rate.value),
                channels=1,  # we only support mono recording
                callback=self._audio_callback,
                blocksize=stream_params.block_size.value,
            )
            self._sd_stream.start()
        except Exception as e:
            logging.error(f"Failed to start audio stream: {e}")
            raise RuntimeError("Audio stream start failed") from e

    def _stop_io(self) -> None:
        try:
            if self._sd_stream is not None:
                self._sd_stream.stop()
                self._sd_stream.close()
                self._sd_stream = None
        except Exception as e:
            logging.error(f"Failed to stop audio stream: {e}")
            raise RuntimeError("Audio stream stop failed") from e

    def _audio_callback(self, indata: SoundBlock, frames: int, time: Any, status: sd.CallbackFlags) -> None:
        """This is called (from a separate thread) for each audio block.
        Note: time is of type CData "PaStreamCallbackTimeInfo *", which is opaque to Python.
        """
        # logging.warning(f"Audio callback called, frames: {frames}, time: {time}")
        if status:
            logging.warning(f"Status: {status}")
        if indata.size > 0:
            # logging.debug(f"Received data: {indata.shape}")
            assert self._sd_stream is not None
            self._audio_buffer.enqueue_sound_block(indata.copy(), self._sd_stream.samplerate)
        else:
            logging.debug("No data in callback.")
