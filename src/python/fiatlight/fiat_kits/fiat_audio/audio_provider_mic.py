import sounddevice as sd  # type: ignore
from typing import Any, Optional
import logging
from .audio_types import SoundBlock, SoundStreamParams
from .audio_provider import AudioProvider


class AudioProviderMic(AudioProvider):
    _sd_stream: Optional[sd.InputStream]

    def __init__(self) -> None:
        super().__init__()
        self._sd_stream = None

    def start(self, stream_params: SoundStreamParams) -> None:
        """Manually start the microphone input, when not using the context manager."""
        self._start_io(stream_params)

    def stop(self) -> None:
        """Manually stop the microphone input, when not using the context manager."""
        self._stop_io()

    def toggle(self, stream_params: SoundStreamParams) -> None:
        """Toggle the microphone input on/off."""
        if self.started():
            self.stop()
        else:
            self.start(stream_params)

    def started(self) -> bool:
        """Check if the microphone input is currently running."""
        return self._sd_stream is not None

    def _start_io(self, stream_params: SoundStreamParams) -> None:
        try:
            self._sd_stream = sd.InputStream(
                samplerate=int(stream_params.sample_rate),
                channels=stream_params.nb_channels,
                callback=self._audio_callback,
                blocksize=stream_params.block_size,
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
