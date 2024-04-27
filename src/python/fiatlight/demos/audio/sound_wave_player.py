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
import sounddevice as sd  # type: ignore
from threading import Thread
from typing import Optional
from fiatlight.demos.audio.sound_wave import SoundWave
from fiatlight.fiat_array import FloatMatrix_Dim1
from fiatlight.fiat_types import TimeSeconds
from typing import Any
import numpy as np
import logging


class SoundWavePlayer:
    # Public attributes
    sound_wave: SoundWave
    position: int = 0
    paused: bool = False

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

    def play_from_start(self) -> None:
        self.stop()
        self.position = 0
        self.paused = False
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
        chunksize: int = min(len(self.sound_wave.wave) - self.position, frames)
        outdata[:chunksize] = self.sound_wave.wave[self.position : self.position + chunksize].reshape(-1, 1)
        outdata[chunksize:] = 0
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
        assert self._stream is not None
        while self._stream.active:
            if self._stop_flag:
                self._stream.stop()
                break
            sd.sleep(100)

    def _pause_impl(self) -> None:
        self.paused = not self.paused
        if self.paused and self._stream is not None:
            self._stream.stop()
            self._stream = None

    def _stop_impl(self) -> None:
        self._stop_flag = True
        try:
            if self._stream is not None:
                self._stream.stop()
        except Exception as e:
            logging.error(f"Error stopping the stream: {str(e)}")
        try:
            if self._thread and self._thread.is_alive():
                self._thread.join()
        except Exception as e:
            logging.error(f"Error joining the thread: {str(e)}")
        self._stream = None
        self._thread = None

    def _seek_impl(self, position: TimeSeconds) -> None:
        try:
            if 0 <= position < self.sound_wave.duration():
                self.position = int(position * self.sound_wave.sample_rate)
            else:
                raise ValueError("Seek position out of bounds")
        except ValueError as e:
            logging.error(f"Seek error: {str(e)}")
            raise e


def create_demo_sound_wave() -> SoundWave:
    """create a wave that plays Do Re Mi Fa Sol La Si Do (0.5 second each)"""
    sample_rate = 44100
    duration_per_note = 0.5  # duration of each note in seconds
    freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

    full_wave = np.array([], dtype=np.float32)
    for freq in freqs:
        samples_per_note = int(sample_rate * duration_per_note)
        time = np.linspace(0, duration_per_note, samples_per_note, endpoint=False)
        wave = np.sin(2 * np.pi * freq * time)
        full_wave = np.concatenate([full_wave, wave])

    return SoundWave(full_wave, sample_rate)  # type: ignore


def sandbox() -> None:
    import time

    sound_wave = create_demo_sound_wave()

    player = SoundWavePlayer(sound_wave)
    # Play "do - re"
    player.play()
    time.sleep(1)  # Wait for 2 notes of 0.5 seconds each to play

    player.pause()
    time.sleep(1)  # Pause for 1 second

    # Seek to "sol" (the fifth note, which starts at 2 seconds into the audio)
    player.seek(TimeSeconds(4 * 0.5))  # 4 notes skipped, each 0.5 seconds long
    player.play()  # Resume playback from "sol"
    time.sleep(2)  # Play "sol - la - si - do", 4 notes of 0.5 seconds each
    player.stop()


if __name__ == "__main__":
    sandbox()
