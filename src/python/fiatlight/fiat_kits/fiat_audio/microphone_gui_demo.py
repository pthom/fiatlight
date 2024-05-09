import fiatlight
from fiatlight import fiat_audio


def sandbox_microphone_gui() -> None:
    fn = fiat_audio.MicrophoneGui()
    fiatlight.fiat_run(fn)


if __name__ == "__main__":
    sandbox_microphone_gui()
