import fiatlight
from fiatlight import fiat_audio


def sandbox_audio_recorder_gui() -> None:
    microphone_gui = fiat_audio.AudioProviderMicGui()
    audio_recorder_gui = fiat_audio.AudioRecorderGui()

    fiatlight.fiat_run_composition([microphone_gui, audio_recorder_gui])


if __name__ == "__main__":
    sandbox_audio_recorder_gui()
