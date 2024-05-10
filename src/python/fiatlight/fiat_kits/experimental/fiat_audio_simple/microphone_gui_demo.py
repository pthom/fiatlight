import fiatlight
from fiatlight.fiat_kits.experimental import fiat_audio_simple


def sandbox_microphone_gui() -> None:
    fn = fiat_audio_simple.MicrophoneGui()
    fiatlight.fiat_run(fn)


if __name__ == "__main__":
    sandbox_microphone_gui()
