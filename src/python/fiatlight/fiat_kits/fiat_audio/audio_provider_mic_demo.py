"""Example usage of the AudioProviderMic class.
This example does not provide a GUI (see audio_provider_mic_gui_demo.py for that).
"""

from fiatlight import fiat_audio


def sandbox() -> None:
    import time
    from fiatlight.fiat_utils import print_repeatable_message

    start = time.time()
    params = fiat_audio.SoundStreamParams(sample_rate=44100, nb_channels=1)  # type: ignore  # noqa
    mic = fiat_audio.AudioProviderMic()
    mic.start(params)
    while time.time() - start < 1.0:
        data = mic.get_sound_blocks()
        print_repeatable_message(f"Received {len(data.blocks)} blocks of audio data.")
    mic.stop()


if __name__ == "__main__":
    sandbox()
