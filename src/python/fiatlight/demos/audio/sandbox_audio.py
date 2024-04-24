from fiatlight.demos.audio.audio_record_gui import AudioRecordGui


def main() -> None:
    import fiatlight

    audio_gui = AudioRecordGui()
    fiatlight.fiat_run(audio_gui)


if __name__ == "__main__":
    main()
