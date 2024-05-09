from .audio_types import (
    SoundWave,
    sound_wave_from_file,
)
from .sound_wave_player import SoundWavePlayer
from .sound_wave_player_gui import SoundWavePlayerGui
from .microphone_gui import MicrophoneGui


def _register_gui_factories() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from .sound_wave_player_gui import SoundWavePlayerGui
    from .audio_types_gui import register_audio_types_gui

    register_type(SoundWave, SoundWavePlayerGui)
    register_audio_types_gui()


_register_gui_factories()


__all__ = [
    "SoundWave",  # A sound wave (a numpy array of floats + a sample rate)
    "sound_wave_from_file",  # Reads a sound wave from a file
    "SoundWavePlayerGui",  # A FunctionWithGui that can play a SoundWave (and outputs nothing)
    "MicrophoneGui",  # A FunctionWithGui that can record sound from a microphone (and outputs a SoundWave)
    "SoundWavePlayer",  # API to play a SoundWave (no GUI)
]
