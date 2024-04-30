from fiatlight.fiat_audio.audio_types import SoundWave, sound_wave_from_file
from fiatlight.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui
from fiatlight.fiat_audio.audio_record_gui import AudioRecordGui


def _register_gui_factories() -> None:
    from fiatlight.fiat_core import gui_factories

    prefix = "fiatlight.fiat_audio."

    from fiatlight.fiat_audio.sound_wave_player_gui import SoundWavePlayerGui

    gui_factories().register_factory(prefix + "sound_wave.SoundWave", SoundWavePlayerGui)

    # from fiatlight.demos.audio.audio_record_gui import AudioRecordGui


_register_gui_factories()


__all__ = ["SoundWave", "SoundWavePlayerGui", "AudioRecordGui", "sound_wave_from_file"]
