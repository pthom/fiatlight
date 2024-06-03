# type: ignore

# pip install librosa matplotlib numpy scipy pedalboard

from fiatlight.fiat_kits.experimental import fiat_audio_simple


def add_chorus_effect(wave: fiat_audio_simple.SoundWave) -> fiat_audio_simple.SoundWave:
    from pedalboard import Pedalboard, Chorus, Reverb  # type: ignore

    # Make a Pedalboard object, containing multiple audio plugins:
    board = Pedalboard([Chorus(), Reverb(room_size=0.25)])

    # Run the audio through our pedalboard:
    effected = board(wave.wave, wave.sample_rate, reset=False)

    return fiat_audio_simple.SoundWave(wave=effected, sample_rate=wave.sample_rate)  # type: ignore


add_chorus_effect.invoke_async = True  # type: ignore


def sandbox() -> None:
    import fiatlight  # noqa

    graph = fiatlight.FunctionsGraph()

    graph.add_function(fiat_audio_simple.MicrophoneGui())

    graph.add_function(add_chorus_effect)
    graph.add_link("MicrophoneGui", "add_chorus_effect")

    fiatlight.run(graph)


if __name__ == "__main__":
    sandbox()
