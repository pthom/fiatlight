from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_types.file_types import (  # noqa
    FilePath,
    FilePath_Save,
    TextPath,
    TextPath_Save,
    ImagePath,
    ImagePath_Save,
    AudioPath,
    AudioPath_Save,
    VideoPath,
    VideoPath_Save,
)
from imgui_bundle import imgui, portable_file_dialogs as pfd
import os.path


########################################################################################################################
#                               File selector
########################################################################################################################
class _BaseFilePathWithGui(AnyDataWithGui[FilePath]):
    """A Gui that enable to select a filename via a file dialog."""

    filters: list[str]
    default_path: str = ""

    _open_file_dialog: pfd.open_file | None = None

    def __init__(self, file_path_type: type) -> None:
        super().__init__(file_path_type)  # noqa
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: FilePath("")
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_str = lambda x: str(x)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False
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


class _BaseFilePathSaveWithGui(AnyDataWithGui[FilePath_Save]):
    """A Gui that enable to select a destination/save filename via a file dialog."""

    filters: list[str]
    default_path: str = ""

    _save_file_dialog: pfd.save_file | None = None

    def __init__(self, file_path_type: type) -> None:
        super().__init__(file_path_type)  # noqa
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: FilePath_Save("")
        self.callbacks.present_str = self.present_str
        self.callbacks.clipboard_copy_str = lambda x: str(x)
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False
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


_ACCEPT_ANY_FILE = "*.*"


class FilePathWithGui(_BaseFilePathWithGui):
    """A Gui that enable to select a filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(FilePath)


class FilePathSaveWithGui(_BaseFilePathSaveWithGui):
    def __init__(self) -> None:
        super().__init__(FilePath_Save)


class ImagePathWithGui(_BaseFilePathWithGui):
    """A Gui that enable to select an image filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(ImagePath)
        self.filters = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga", _ACCEPT_ANY_FILE]


class ImagePathSaveWithGui(_BaseFilePathSaveWithGui):
    """A Gui that enable to select a destination/save image filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(ImagePath_Save)
        self.filters = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga", _ACCEPT_ANY_FILE]


class TextPathWithGui(_BaseFilePathWithGui):
    """A Gui that enable to select a text filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(TextPath)
        self.filters = ["*.txt, *.*"]


class TextPathSaveWithGui(_BaseFilePathSaveWithGui):
    """A Gui that enable to select a destination/save text filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(TextPath_Save)
        self.filters = ["*.txt, *.*"]


class AudioPathWithGui(_BaseFilePathWithGui):
    """A Gui that enable to select an audio filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(AudioPath)
        self.filters = ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.aiff", "*.m4a", _ACCEPT_ANY_FILE]


class AudioPathSaveWithGui(_BaseFilePathSaveWithGui):
    """A Gui that enable to select a destination/save audio filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(AudioPath_Save)
        self.filters = ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.aiff", "*.m4a", _ACCEPT_ANY_FILE]


class VideoPathWithGui(_BaseFilePathWithGui):
    """A Gui that enable to select a video filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(VideoPath)
        self.filters = ["*.mp4", "*.avi", "*.mkv", _ACCEPT_ANY_FILE]


class VideoPathSaveWithGui(_BaseFilePathSaveWithGui):
    """A Gui that enable to select a destination/save video filename via a file dialog."""

    def __init__(self) -> None:
        super().__init__(VideoPath_Save)
        self.filters = ["*.mp4", "*.avi", "*.mkv", _ACCEPT_ANY_FILE]


########################################################################################################################
#                               Register all types
########################################################################################################################
def _register_file_paths_types() -> None:
    from fiatlight.fiat_togui.gui_registry import register_typing_new_type

    register_typing_new_type(FilePath, FilePathWithGui)
    register_typing_new_type(TextPath, TextPathWithGui)
    register_typing_new_type(ImagePath, ImagePathWithGui)
    register_typing_new_type(AudioPath, AudioPathWithGui)
    register_typing_new_type(VideoPath, VideoPathWithGui)
    register_typing_new_type(FilePath_Save, FilePathSaveWithGui)
    register_typing_new_type(TextPath_Save, TextPathSaveWithGui)
    register_typing_new_type(ImagePath_Save, ImagePathSaveWithGui)
    register_typing_new_type(AudioPath_Save, AudioPathSaveWithGui)
    register_typing_new_type(VideoPath_Save, VideoPathSaveWithGui)


def text_from_file(path: TextPath) -> str | None:
    try:
        with open(path, "r") as f:
            r = f.read()
        return r
    except OSError:
        return None


class TextToFileGui(FunctionWithGui):
    _save_dialog: pfd.save_file | None = None
    _text: str | None = None

    def __init__(self) -> None:
        super().__init__(self.f, "TextToFile")
        self.internal_state_gui = self._internal_state_gui

    def f(self, text: str) -> None:
        self._text = text

    def do_write(self, path: FilePath_Save) -> None:
        assert self._text is not None
        with open(path, "w") as f:
            f.write(self._text)

    def _internal_state_gui(self) -> bool:
        if self._text is None:
            return False
        if imgui.button("Save file"):
            self._save_dialog = pfd.save_file("Select file", "", ["*.txt", _ACCEPT_ANY_FILE])
        if self._save_dialog is not None and self._save_dialog.ready():
            selected_file = self._save_dialog.result()
            self.do_write(selected_file)  # type: ignore
            self._save_dialog = None
        return False
