"""A class that plays a SoundWave object.
Usage:
    player = SoundWavePlayer(sound_wave)
    player.play()
    time.sleep(1)  # Play for 1 second

    player.pause()
    player.seek(5.0)

    player.play()
    time.sleep(2)  # Play for 2 seconds
    player.stop()
"""

from typing import Any
import time
import logging
import sounddevice as sd  # type: ignore
from typing import Optional
from .audio_types import SoundData
from fiatlight.fiat_types import TimeSeconds
import threading

from .audio_types import SoundWave


class SoundWavePlayer:
    # Public attributes
    sound_wave: SoundWave
    position: int = 0
    paused: bool = False
    _volume: float = 1.0
    _lock: threading.Lock
    VOLUME_MAX = 2.0

    # Private attributes
    _stop_flag: bool = False
    _stream: Optional[sd.OutputStream] = None

    #
    # Public API
    #
    def __init__(self, sound_wave: SoundWave) -> None:
        self.sound_wave: SoundWave = sound_wave
        self._init_stream()
        self._lock = threading.Lock()

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        if value < 0:
            value = 0
        elif value > self.VOLUME_MAX:
            value = self.VOLUME_MAX
        self._volume = value

    def stop(self) -> None:
        self._stop_impl()

    def seek(self, position: TimeSeconds) -> None:
        self._seek_impl(position)

    def is_playing(self) -> bool:
        return self._stream.active if self._stream else False  # type: ignore

    def position_seconds(self) -> TimeSeconds:
        return TimeSeconds(self.position / self.sound_wave.sample_rate)

    def play(self) -> None:
        self._play_impl()

    def pause(self) -> None:
        self._pause_impl()

    def reset_player(self) -> None:
        self.stop()
        with self._lock:
            self.position = 0
            self.paused = True
        self._init_stream()

    def can_advance(self, seconds: float) -> bool:
        return self.position + seconds * self.sound_wave.sample_rate < len(self.sound_wave.wave)

    def can_rewind(self, seconds: float) -> bool:
        return self.position - seconds * self.sound_wave.sample_rate >= 0

    def advance(self, seconds: TimeSeconds) -> None:
        self.seek(TimeSeconds(self.position_seconds() + seconds))

    def rewind(self, seconds: TimeSeconds) -> None:
        self.seek(TimeSeconds(self.position_seconds() - seconds))

    # end::tagname[]

    #
    # Private methods
    #
    def _init_stream(self) -> None:
        try:
            if self._stream is not None:
                self._stream.close()
            self._stream = sd.OutputStream(
                samplerate=self.sound_wave.sample_rate,
                channels=self.sound_wave.nb_channels(),
                callback=self._callback,
                blocksize=1024,
            )
        except Exception as e:
            logging.error(f"Error initializing the stream: {str(e)}")
            raise RuntimeError("Stream initialization failed") from e

    def _callback(self, outdata: SoundData, nb_asked_frames: int, _time: Any, _status: sd.CallbackFlags) -> None:
        with self._lock:
            if self._stop_flag:
                raise sd.CallbackStop
            if self.paused:
                outdata.fill(0)
                return

            remaining_frames = len(self.sound_wave.wave) - self.position
            chunksize = min(remaining_frames, nb_asked_frames)

            if chunksize <= 0:
                outdata.fill(0)
                raise sd.CallbackStop

            # Safeguard to ensure we don't exceed the buffer size
            if outdata.shape[0] < chunksize:
                logging.warning(f"SoundWavePlayer._callback: Buffer size too small: {outdata.shape[0]=} < {chunksize=}")
                chunksize = outdata.shape[0]

            if chunksize <= 0:
                raise sd.CallbackStop

            # Take into account if the wave is stereo
            if len(self.sound_wave.wave.shape) > 1 and self.sound_wave.wave.shape[1] == 2:
                # Assuming the outdata buffer is also set up for stereo playback
                outdata[:chunksize] = self.sound_wave.wave[self.position : self.position + chunksize] * self.volume
            else:
                # Mono playback
                outdata[:chunksize] = (
                    self.sound_wave.wave[self.position : self.position + chunksize].reshape(chunksize, -1) * self.volume
                )
            outdata[chunksize:] = 0  # Fill the rest of the buffer with zeros

            self.position += chunksize

            # logging.warning(f"Playback position: {self.position}/{len(self.sound_wave.wave)} frames")

    def _play_impl(self) -> None:
        with self._lock:
            self.paused = False
            self._stop_flag = False

            if self.position >= len(self.sound_wave.wave):
                self.position = 0

            try:
                if self._stream is None or not self._stream.active:
                    self._init_stream()
                assert self._stream is not None
                self._stream.start()
            except Exception as e:
                logging.error(f"Error starting the stream: {str(e)}")
                return

    def _pause_impl(self) -> None:
        with self._lock:
            self.paused = not self.paused
        if self.paused and self._stream is not None:
            self._stream.stop()
            self._stream = None

    def _stop_impl(self) -> None:
        with self._lock:
            if self._stop_flag:
                return
            self._stop_flag = True
        time.sleep(0.1)  # Wait for the callback to finish
        try:
            if self._stream is not None:
                self._stream.stop()
        except Exception as e:
            logging.error(f"Error stopping the stream: {str(e)}")
        with self._lock:
            self._stream = None

    def _seek_impl(self, position: TimeSeconds) -> None:
        with self._lock:
            try:
                if 0 <= position <= self.sound_wave.duration():
                    self.position = int(position * self.sound_wave.sample_rate)
                else:
                    logging.error(f"Seek position out of bounds: {position}, duration: {self.sound_wave.duration()}")
            except ValueError as e:
                logging.error(f"Seek error: {str(e)}")
                raise e
