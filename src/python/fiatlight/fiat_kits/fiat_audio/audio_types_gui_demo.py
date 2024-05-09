import fiatlight
from fiatlight import fiat_audio


def sandbox() -> None:
    """A simple demo that shows we can edit audio types in the GUI."""

    def my_function(
        sample_rate: fiat_audio.SampleRate, nb_channels: fiat_audio.NbChannels, block_size: fiat_audio.BlockSize
    ) -> None:
        pass

    fiatlight.fiat_run(my_function)


if __name__ == "__main__":
    sandbox()
