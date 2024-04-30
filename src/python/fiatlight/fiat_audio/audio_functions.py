from fiatlight.fiat_audio.audio_types import SoundWave, SampleRate
from fiatlight.fiat_array import FloatMatrix_Dim1
import sounddevice  # type: ignore
import logging


def record_audio(duration: float, sample_rate: SampleRate) -> SoundWave:
    logging.info(f"Recording audio for {duration} seconds at {sample_rate} Hz...")
    audio = sounddevice.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sounddevice.wait()  # Wait until recording is finished
    print("Recording complete.")
    audio_flat: FloatMatrix_Dim1 = audio.flatten()
    return SoundWave(audio_flat, sample_rate)


def play_audio(sound_wave: SoundWave) -> None:
    logging.info(f"Playing audio with duration {sound_wave.duration()} seconds at {sound_wave.sample_rate} Hz...")
    sounddevice.play(sound_wave.wave, sound_wave.sample_rate)
    sounddevice.wait()  # Wait until the sound has finished playing
    logging.info("Audio playback complete.")
