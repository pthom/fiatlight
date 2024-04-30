from fiatlight.fiat_audio.audio_types import SoundBlock, SampleRate, NbChannels, BlockSize
from fiatlight.fiat_audio.wip_audio_provider import AudioProvider
import sounddevice as sd  # type: ignore
from queue import Queue, Empty
from typing import Any, List, Optional
import logging
from dataclasses import dataclass


@dataclass
class MicrophoneParams:
    sample_rate: SampleRate = SampleRate(44100)
    nb_channels: NbChannels = NbChannels(1)
    block_size: BlockSize = BlockSize(512)


class MicrophoneIo(AudioProvider):
    params: MicrophoneParams
    _queue: Queue[SoundBlock]
    _stream: Optional[sd.InputStream]

    def __init__(self, params: MicrophoneParams) -> None:
        self.params = params
        self._queue = Queue()
        self._stream = None

    def start(self) -> None:
        """Manually start the microphone input, when not using the context manager."""
        self._start_io()

    def stop(self) -> None:
        """Manually stop the microphone input, when not using the context manager."""
        self._stop_io()

    def toggle(self) -> None:
        """Toggle the microphone input on/off."""
        if self.started():
            self.stop()
        else:
            self.start()

    def started(self) -> bool:
        """Check if the microphone input is currently running."""
        return self._stream is not None

    def __enter__(self) -> "MicrophoneIo":
        self._start_io()
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[Exception], traceback: Optional[Any]) -> None:
        self._stop_io()

    def _start_io(self) -> None:
        try:
            self._stream = sd.InputStream(
                samplerate=int(self.params.sample_rate),
                channels=self.params.nb_channels,
                callback=self._audio_callback,
                blocksize=self.params.block_size,
            )
            self._stream.start()
        except Exception as e:
            logging.error(f"Failed to start audio stream: {e}")
            raise RuntimeError("Audio stream start failed") from e

    def _stop_io(self) -> None:
        try:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
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
            self._queue.put(indata.copy())
        else:
            logging.debug("No data in callback.")

    def get_sound_blocks(self) -> List[SoundBlock]:
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
        return blocks


def sandbox() -> None:
    """Example usage of the MicrophoneIo class."""
    import time
    from fiatlight.fiat_utils import print_repeatable_message

    start = time.time()
    params = MicrophoneParams(sample_rate=44100, nb_channels=1)  # type: ignore  # noqa
    with MicrophoneIo(params) as mic:
        while time.time() - start < 1.0:
            data = mic.get_sound_blocks()
            print_repeatable_message(f"Received {len(data)} blocks of audio data.")


if __name__ == "__main__":
    sandbox()
