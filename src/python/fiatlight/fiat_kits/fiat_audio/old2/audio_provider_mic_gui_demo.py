import fiatlight
from fiatlight import fiat_audio


def sandbox() -> None:
    fn = fiat_audio.AudioProviderMicGui()
    fiatlight.fiat_run(fn)


if __name__ == "__main__":
    sandbox()
