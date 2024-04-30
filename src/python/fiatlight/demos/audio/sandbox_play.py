def sandbox_play_file() -> None:
    import fiatlight
    from fiatlight.fiat_audio.audio_types import sound_wave_from_file

    fiatlight.fiat_run(sound_wave_from_file)


if __name__ == "__main__":
    sandbox_play_file()
