from fiatlight.demos.audio.sound_wave import SoundWave, sound_wave_from_file
from fiatlight.demos.audio.sound_wave_gui import SoundWaveGui
from fiatlight.demos.audio.audio_record_gui import AudioRecordGui


def _register_gui_factories() -> None:
    from fiatlight.fiat_core import gui_factories

    prefix = "fiatlight.demos.audio."

    from fiatlight.demos.audio.sound_wave_gui import SoundWaveGui

    gui_factories().register_factory(prefix + "sound_wave.SoundWave", SoundWaveGui)

    # from fiatlight.demos.audio.audio_record_gui import AudioRecordGui


_register_gui_factories()


__all__ = ["SoundWave", "SoundWaveGui", "AudioRecordGui", "sound_wave_from_file"]
