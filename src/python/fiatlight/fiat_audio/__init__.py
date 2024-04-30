from fiatlight.fiat_audio.audio_types import SoundWave, sound_wave_from_file
from fiatlight.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui
from fiatlight.fiat_audio.audio_record_gui import AudioRecordGui


def _register_gui_factories() -> None:
    from fiatlight.fiat_core import gui_factories
    from fiatlight.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui
    from fiatlight.fiat_audio.audio_types_gui import register_audio_types_gui

    prefix = "fiatlight.fiat_audio."
    gui_factories().register_factory(prefix + "sound_wave.SoundWave", SoundWavePlayerGui)
    register_audio_types_gui()


_register_gui_factories()


__all__ = ["SoundWave", "SoundWavePlayerGui", "AudioRecordGui", "sound_wave_from_file"]
