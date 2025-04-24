"""Demonstrates playing a sound wave from a file using SoundWavePlayerGui"""

import fiatlight
from fiatlight.fiat_kits.experimental import fiat_audio_simple


def main() -> None:
    fiatlight.run(fiat_audio_simple.sound_wave_from_file, app_name="Sound Wave Player Demo")


if __name__ == "__main__":
    main()
