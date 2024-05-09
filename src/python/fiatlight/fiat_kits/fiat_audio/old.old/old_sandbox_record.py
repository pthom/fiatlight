def sandbox_record() -> None:
    import fiatlight
    from fiatlight.fiat_kits.fiat_audio.old.audio_record_gui_old import AudioRecordGui

    audio_gui = AudioRecordGui()
    fiatlight.fiat_run(audio_gui)


if __name__ == "__main__":
    sandbox_record()
