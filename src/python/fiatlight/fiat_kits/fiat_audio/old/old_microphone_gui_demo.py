import fiatlight
from fiatlight import fiat_audio


def sandbox_microphone_params() -> None:
    def my_function(params: fiat_audio.SoundStreamParams) -> None:
        pass

    # register_microphone_params_gui()
    fiatlight.fiat_run(my_function)


def sandbox_microphone_gui() -> None:
    from fiatlight.fiat_kits.fiat_audio.old.old_microphone_gui import MicrophoneGui

    # fn = fiat_audio.MicrophoneGui()
    fn = MicrophoneGui()
    fiatlight.fiat_run(fn)


if __name__ == "__main__":
    # sandbox_microphone_params()
    sandbox_microphone_gui()
