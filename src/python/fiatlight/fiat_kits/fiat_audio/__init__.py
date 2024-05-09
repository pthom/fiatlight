from .audio_types import (
    SoundWave,
    sound_wave_from_file,
    SampleRate,
    NbChannels,
    BlockSize,
    SoundBlocksList,
    SoundStreamParams,
)
from .audio_provider import AudioProvider  # abstract
from .audio_provider_gui import AudioProviderGui  # abstract
from .audio_provider_mic import AudioProviderMic
from .audio_provider_mic_gui import AudioProviderMicGui
from .audio_recorder_gui import AudioRecorderGui
from .sound_wave_player import SoundWavePlayer
from .sound_wave_player_gui import SoundWavePlayerGui


def _register_gui_factories() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_kits.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui
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
    "SoundBlocksList",
    "SoundStreamParams",
    # from audio_provider
    "AudioProvider",  # abstract interface
    # from audio_provider_gui
    "AudioProviderGui",  # abstract interface
    # from audio_provider_mic
    "AudioProviderMic",
    "SoundStreamParams",
    # from audio_provider_mic_gui
    "AudioProviderMicGui",
    # from microphone_io
    "AudioProviderMic",
    "SoundStreamParams",
    # from audio_recorder_gui
    "AudioRecorderGui",
    # from sound_wave_player
    "SoundWavePlayer",
    # from sound_wave_player_gui
    "SoundWavePlayerGui",
]
