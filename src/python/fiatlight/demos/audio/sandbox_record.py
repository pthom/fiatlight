def sandbox_record() -> None:
    import fiatlight
    from fiatlight.fiat_audio.audio_record_gui import AudioRecordGui

    audio_gui = AudioRecordGui()
    fiatlight.fiat_run(audio_gui)


if __name__ == "__main__":
    sandbox_record()
