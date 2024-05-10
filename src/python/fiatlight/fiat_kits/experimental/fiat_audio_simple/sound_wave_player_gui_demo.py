"""Demonstrates playing a sound wave from a file using SoundWavePlayerGui"""

import fiatlight
from fiatlight import fiat_audio_simple


def sandbox_play_file() -> None:
    fiatlight.fiat_run(fiat_audio_simple.sound_wave_from_file)


if __name__ == "__main__":
    sandbox_play_file()
