from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from .file_types import FilePath, FilePath_Save
from imgui_bundle import imgui, portable_file_dialogs as pfd
import os.path


########################################################################################################################
#                               File selector
########################################################################################################################
class FilePathWithGui(AnyDataWithGui[FilePath]):
    filters: list[str]
    default_path: str = ""

    _open_file_dialog: pfd.open_file | None = None

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: FilePath("")
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_str = lambda x: str(x)
        self.callbacks.clipboard_copy_possible = True
        self.filters = []

    def edit(self, value: FilePath) -> tuple[bool, FilePath]:
        from fiatlight.fiat_widgets import fiat_osd

        changed = False
        if imgui.button("Select file"):
            self._open_file_dialog = pfd.open_file("Select file", self.default_path, self.filters)
        if self._open_file_dialog is not None and self._open_file_dialog.ready():
            if len(self._open_file_dialog.result()) == 1:
                selected_file = self._open_file_dialog.result()[0]
                value = FilePath(selected_file)
                changed = True
            self._open_file_dialog = None
        if len(value) > 0:
            basename = os.path.basename(value)
            imgui.same_line()
            imgui.text(basename)
            fiat_osd.set_widget_tooltip(value)
        return changed, value

    @staticmethod
    def present_str(value: FilePath) -> str:
        from pathlib import Path

        # Returns two lines: the file name and the full path
        # (which will be presented as a tooltip)
        try:
            as_path = Path(value)
            r = str(as_path.name) + "\n"
            r += str(as_path.absolute())
            return r
        except TypeError:
            return "???"


class FilePathSaveWithGui(AnyDataWithGui[FilePath_Save]):
    filters: list[str]
    default_path: str = ""

    _save_file_dialog: pfd.save_file | None = None

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: FilePath_Save("")
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_str = lambda x: str(x)
        self.callbacks.clipboard_copy_possible = True
        self.filters = []

    def edit(self, value: FilePath_Save) -> tuple[bool, FilePath_Save]:
        from fiatlight.fiat_widgets import fiat_osd

        changed = False
        if imgui.button("Select save file"):
            self._save_file_dialog = pfd.save_file("Select file", self.default_path, self.filters)
        if self._save_file_dialog is not None and self._save_file_dialog.ready():
            selected_file = self._save_file_dialog.result()
            value = FilePath_Save(selected_file)
            changed = True
            self._open_file_dialog = None

        if len(value) > 0:
            basename = os.path.basename(value)
            imgui.same_line()
            imgui.text(basename)
            fiat_osd.set_widget_tooltip(value)
        return changed, value

    @staticmethod
    def present_str(value: FilePath_Save) -> str:
        from pathlib import Path

        # Returns two lines: the file name and the full path
        # (which will be presented as a tooltip)
        try:
            as_path = Path(value)
            r = str(as_path.name) + "\n"
            r += str(as_path.absolute())
            return r
        except TypeError:
            return "???"


class ImagePathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]


class ImagePathSaveWithGui(FilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"]


class TextPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.txt, *.*"]


class TextPathSaveWithGui(FilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.txt, *.*"]


class AudioPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.aiff", "*.m4a"]


class AudioPathSaveWithGui(FilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.aiff", "*.m4a"]


class VideoPathWithGui(FilePathWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.mp4", "*.avi", "*.mkv"]


class VideoPathSaveWithGui(FilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__()
        self.filters = ["*.mp4", "*.avi", "*.mkv"]


########################################################################################################################
#                               Register all types
########################################################################################################################
def _register_file_paths_types() -> None:
    from fiatlight.fiat_togui.to_gui import register_type
    from fiatlight.fiat_types import (
        # Open file types
        FilePath,
        TextPath,
        ImagePath,
        AudioPath,
        VideoPath,
        # Save file types
        FilePath_Save,
        TextPath_Save,
        ImagePath_Save,
        AudioPath_Save,
        VideoPath_Save,
    )

    register_type(FilePath, FilePathWithGui)
    register_type(TextPath, TextPathWithGui)
    register_type(ImagePath, ImagePathWithGui)
    register_type(AudioPath, AudioPathWithGui)
    register_type(VideoPath, VideoPathWithGui)
    register_type(FilePath_Save, FilePathSaveWithGui)
    register_type(TextPath_Save, TextPathSaveWithGui)
    register_type(ImagePath_Save, ImagePathSaveWithGui)
    register_type(AudioPath_Save, AudioPathSaveWithGui)
    register_type(VideoPath_Save, VideoPathSaveWithGui)
