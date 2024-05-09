import sounddevice as sd  # type: ignore
from typing import Any, Optional
import logging
from .audio_types import SoundBlock, SoundStreamParams
from .audio_provider import AudioProvider


class AudioProviderMic(AudioProvider):
    _sd_stream: Optional[sd.InputStream]

    def __init__(self, sound_stream_params: SoundStreamParams) -> None:
        super().__init__(sound_stream_params)
        self._sd_stream = None

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
        return self._sd_stream is not None

    def __enter__(self) -> "AudioProviderMic":
        self._start_io()
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[Exception], traceback: Optional[Any]) -> None:
        self._stop_io()

    def _start_io(self) -> None:
        try:
            self._sd_stream = sd.InputStream(
                samplerate=int(self.stream_params.sample_rate),
                channels=self.stream_params.nb_channels,
                callback=self._audio_callback,
                blocksize=self.stream_params.block_size,
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
            self._queue.put(indata.copy())
        else:
            logging.debug("No data in callback.")
