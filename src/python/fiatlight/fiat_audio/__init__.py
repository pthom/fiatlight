from fiatlight.fiat_audio.audio_types import SoundWave, sound_wave_from_file
from fiatlight.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui
from fiatlight.fiat_audio.audio_record_gui_old import AudioRecordGui


def _register_gui_factories() -> None:
    from fiatlight.fiat_core.to_gui import register_type
    from fiatlight.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui
    from fiatlight.fiat_audio.audio_types_gui import register_audio_types_gui

    register_type(SoundWave, SoundWavePlayerGui)
    register_audio_types_gui()


_register_gui_factories()


__all__ = ["SoundWave", "SoundWavePlayerGui", "AudioRecordGui", "sound_wave_from_file"]
