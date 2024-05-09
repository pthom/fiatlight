import fiatlight


def sandbox() -> None:
    """A simple demo that shows we can edit audio types in the GUI."""
    from fiatlight.fiat_kits.fiat_audio.audio_types import SampleRate, BlockSize, NbChannels

    def my_function(sample_rate: SampleRate, nb_channels: NbChannels, block_size: BlockSize) -> None:
        pass

    fiatlight.fiat_run(my_function)


if __name__ == "__main__":
    sandbox()
