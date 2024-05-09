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
import numpy as np
import logging
import sounddevice as sd  # type: ignore
from threading import Thread, current_thread
from typing import Optional
from fiatlight.fiat_kits.fiat_array import FloatMatrix_Dim1
from fiatlight.fiat_types import TimeSeconds

from fiatlight.fiat_kits.fiat_audio.sound_wave import SoundWave


class SoundWavePlayer:
    # Public attributes
    sound_wave: SoundWave
    position: int = 0
    paused: bool = False
    _volume: float = 1.0
    VOLUME_MAX = 2.0

    # Private attributes
    _stop_flag: bool = False
    _stream: Optional[sd.OutputStream] = None
    _thread: Optional[Thread] = None

    #
    # Public API
    #
    def __init__(self, sound_wave: SoundWave) -> None:
        self.sound_wave: SoundWave = sound_wave
        self._init_stream()

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
            self._stream = sd.OutputStream(samplerate=self.sound_wave.sample_rate, channels=1, callback=self._callback)
        except Exception as e:
            logging.error(f"Error initializing the stream: {str(e)}")
            raise RuntimeError("Stream initialization failed") from e

    def _callback(self, outdata: FloatMatrix_Dim1, frames: int, _time: Any, _status: sd.CallbackFlags) -> None:
        if self._stop_flag:
            raise sd.CallbackStop
        if self.paused:
            outdata.fill(0)
            return

        remaining_frames = len(self.sound_wave.wave) - self.position
        chunksize = min(remaining_frames, frames)

        # Safeguard to ensure we don't exceed the buffer size
        if outdata.shape[0] < chunksize:
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

    def _play_impl(self) -> None:
        self.paused = False
        self._stop_flag = False
        try:
            if self._stream is None or not self._stream.active:
                self._init_stream()
            assert self._stream is not None
            self._stream.start()
        except Exception as e:
            logging.error(f"Error starting the stream: {str(e)}")
            return
        if self._thread is None or not self._thread.is_alive():
            try:
                self._thread = Thread(target=self._stream_monitor)
                self._thread.start()
            except Exception as e:
                logging.error(f"Error starting the monitor thread: {str(e)}")

    def _stream_monitor(self) -> None:
        """Monitor the stream and trigger a reset when the end is reached."""
        while self._stream is not None and self._stream.active:
            if self._stop_flag:
                break
            if self.position >= len(self.sound_wave.wave):
                self.reset_player()  # Reset the player when end of wave is reached
                break
            sd.sleep(100)

    def _pause_impl(self) -> None:
        self.paused = not self.paused
        if self.paused and self._stream is not None:
            self._stream.stop()
            self._stream = None

    def _stop_impl(self) -> None:
        if self._stop_flag:
            return
        self._stop_flag = True
        time.sleep(0.1)  # Wait for the callback to finish
        try:
            if self._stream is not None:
                self._stream.stop()
        except Exception as e:
            logging.error(f"Error stopping the stream: {str(e)}")
        # Only join the thread if it's not the current thread
        if self._thread is not None and self._thread.is_alive():
            if self._thread.ident != current_thread().ident:
                try:
                    self._thread.join()
                except Exception as e:
                    logging.error(f"Error joining the thread: {str(e)}")
            else:
                pass
                # logging.debug("Attempted to join the current thread; skipping join call.")
        self._stream = None
        self._thread = None

    def _seek_impl(self, position: TimeSeconds) -> None:
        try:
            if 0 <= position <= self.sound_wave.duration():
                self.position = int(position * self.sound_wave.sample_rate)
            else:
                logging.error(f"Seek position out of bounds: {position}, duration: {self.sound_wave.duration()}")
        except ValueError as e:
            logging.error(f"Seek error: {str(e)}")
            raise e


def create_demo_sound_wave() -> SoundWave:
    """create a wave that plays Do Re Mi Fa Sol La Si Do (0.5 second each)"""
    sample_rate = 44100
    duration_per_note = 0.5  # duration of each note in seconds
    freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

    full_wave = np.array([], dtype=np.float32)
    for i in range(50):
        for freq in freqs:
            samples_per_note = int(sample_rate * duration_per_note)
            time = np.linspace(0, duration_per_note, samples_per_note, endpoint=False)
            wave = np.sin(2 * np.pi * freq * time)
            full_wave = np.concatenate([full_wave, wave])

    return SoundWave(full_wave, sample_rate)  # type: ignore
