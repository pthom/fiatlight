import fiatlight
from fiatlight.fiat_kits.experimental import fiat_audio_simple


def main() -> None:
    fn = fiat_audio_simple.MicrophoneGui()
    fiatlight.run(fn)


if __name__ == "__main__":
    main()
