# type: ignore
# (pedalboard is not typed)

import pedalboard.io

from fiatlight import FunctionWithGui
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_types import format_time_seconds, AudioPath
from fiatlight.fiat_kits.experimental.fiat_audio_simple import SoundWave
from imgui_bundle import imgui
from imgui_bundle import portable_file_dialogs as pfd
import os

# song = "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/priv_assets/audio/6 - Libera me.mp3"
# song = "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/priv_assets/audio/01 Rolling In the Deep.m4a"
#
# with pedalboard.io.AudioFile(song, "r") as f:
#     print(f.duration)  # => 30.0
#     print(f.samplerate)  # => 44100
#     print(f.num_channels)  # => 2
#     print(f.read(f.samplerate * 10))
#     print(f.duration)  # => 30.0


def open_audio_file(audio_path: AudioPath) -> pedalboard.io.ReadableAudioFile:
    return pedalboard.io.ReadableAudioFile(audio_path)


def save_audio_file(in_audio_file: pedalboard.io.ReadableAudioFile, audio_path: AudioPath) -> None:
    current_position = in_audio_file.tell()
    in_audio_file.seek(0)
    with pedalboard.io.AudioFile(audio_path, "w", in_audio_file.samplerate, in_audio_file.num_channels) as o:
        while in_audio_file.tell() < in_audio_file.frames:
            o.write(in_audio_file.read(1024))
    in_audio_file.seek(current_position)


def readable_audio_file_to_sound_wave(data: pedalboard.io.ReadableAudioFile) -> SoundWave:
    data.seek(0)
    nb_frame = data.frames
    wave = data.read(nb_frame)
    r = SoundWave(wave=wave, sample_rate=data.samplerate)
    return r


class ReadableAudioFileWithGui(AnyDataWithGui[pedalboard.io.ReadableAudioFile]):
    _save_file_dialog: pfd.save_file | None = None

    def __init__(self) -> None:
        super().__init__(pedalboard.io.ReadableAudioFile)
        self.callbacks.present_str = self.present_str
        self.callbacks.present = self.present

    @staticmethod
    def present_str(data: pedalboard.io.ReadableAudioFile) -> str:
        filename = os.path.basename(data.name)
        duration_str = format_time_seconds(data.duration)  # noqa
        r = f"{filename} - {duration_str}"
        return r

    def present(self, data: pedalboard.io.ReadableAudioFile) -> None:
        info = f"{data.samplerate/1000}kHz - {data.num_channels} channels"
        imgui.text(info)


class SaveAudioFileGui(FunctionWithGui):
    in_audio_file: pedalboard.io.ReadableAudioFile | None = None
    _save_file_dialog: pfd.save_file | None = None

    def __init__(self):
        super().__init__(self.f, "Save audio file")
        self.internal_state_gui = self.internal_state_gui

    def f(self, in_audio_file: pedalboard.io.ReadableAudioFile | None) -> None:
        self.in_audio_file = in_audio_file

    def internal_state_gui(self) -> None:
        if self.in_audio_file is None:
            return
        dialog_opened = self._save_file_dialog is not None
        imgui.begin_disabled(dialog_opened)
        if imgui.button("Save audio file"):
            self._save_file_dialog = pfd.save_file("Save audio file", "", ["*.wav", "*.mp3", "*.ogg", "*.flac"])
        if self._save_file_dialog is not None:
            if self._save_file_dialog.ready():
                filename = self._save_file_dialog.result()
                save_audio_file(self.in_audio_file, filename)  # noqa
                self._save_file_dialog = None
        imgui.end_disabled()


def main() -> None:
    import fiatlight  # noqa

    fiatlight.register_type(pedalboard.io.ReadableAudioFile, ReadableAudioFileWithGui)

    graph = fiatlight.FunctionsGraph()

    graph.add_function(open_audio_file)
    graph.add_function(SaveAudioFileGui())
    graph.add_function(readable_audio_file_to_sound_wave)
    graph.add_link("open_audio_file", "Save audio file")
    graph.add_link("open_audio_file", "readable_audio_file_to_sound_wave")

    fiatlight.run(graph)


if __name__ == "__main__":
    main()
