import fiatlight
from fiatlight import fiat_audio


def sandbox_play_file() -> None:
    fiatlight.fiat_run(fiat_audio.sound_wave_from_file)


if __name__ == "__main__":
    sandbox_play_file()
