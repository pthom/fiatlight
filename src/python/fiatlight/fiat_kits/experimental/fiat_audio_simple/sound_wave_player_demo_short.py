"""Demonstrates how to use the SoundWavePlayer class to play a sound wave.
This example does not provide a GUI. It's simply plays notes.
"""

from fiatlight.fiat_kits.experimental import fiat_audio_simple
import numpy as np


def create_demo_sound_wave() -> fiat_audio_simple.SoundWave:
    """create a wave that plays Do Re Mi Fa Sol La Si Do (0.5 second each)"""
    sample_rate = 44100
    duration_per_note = 0.1  # duration of each note in seconds
    freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

    full_wave = np.array([], dtype=np.float32)
    for i in range(3):
        for freq in freqs:
            samples_per_note = int(sample_rate * duration_per_note)
            time = np.linspace(0, duration_per_note, samples_per_note, endpoint=False)
            wave = np.sin(2 * np.pi * freq * time)
            full_wave = np.concatenate([full_wave, wave])

    return fiat_audio_simple.SoundWave(full_wave, sample_rate)


def sandbox() -> None:
    sound_wave = create_demo_sound_wave()
    player = fiat_audio_simple.SoundWavePlayer(sound_wave)
    player.play()


if __name__ == "__main__":
    sandbox()
