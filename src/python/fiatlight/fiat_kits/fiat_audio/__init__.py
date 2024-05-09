from .audio_types import (
    SampleRate,
    NbChannels,
    BlockSize,
    SoundStreamParams,
)
from .sound_wave import SoundWave, sound_wave_from_file
from .audio_buffer import AudioBuffer  # abstract
from .audio_provider_mic import AudioProviderMic


def _register_gui_factories() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_kits.fiat_audio.old2.sound_wave_player_gui import SoundWavePlayerGui
    from fiatlight.fiat_kits.fiat_audio.audio_types_gui import register_audio_types_gui

    register_type(SoundWave, SoundWavePlayerGui)
    register_audio_types_gui()


_register_gui_factories()


__all__ = [
    # from audio_types
    "SoundWave",
    "sound_wave_from_file",
    "SampleRate",
    "NbChannels",
    "BlockSize",
    "SoundStreamParams",
    # from sound_wave
    "SoundWave",
    "sound_wave_from_file",
    # from audio_provider
    "AudioBuffer",
    # from audio_provider_mic
    "AudioProviderMic",
    "SoundStreamParams",
    # from microphone_io
    "AudioProviderMic",
    "SoundStreamParams",
]
