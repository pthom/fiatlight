"""Demonstrates how to use the SoundWavePlayer class to play a sound wave.
This example does not provide a GUI. It's simply plays notes.
"""

from fiatlight.fiat_kits.experimental import fiat_audio_simple
from fiatlight.fiat_types import TimeSeconds
import numpy as np


def create_demo_sound_wave() -> fiat_audio_simple.SoundWave:
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

    return fiat_audio_simple.SoundWave(full_wave, sample_rate)


def sandbox() -> None:
    import time

    sound_wave = create_demo_sound_wave()
    # sound_wave = sound_wave_from_file(
    #     "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/priv_assets/audio/3 - Sanctus.mp3"  # type: ignore
    # )

    player = fiat_audio_simple.SoundWavePlayer(sound_wave)
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
