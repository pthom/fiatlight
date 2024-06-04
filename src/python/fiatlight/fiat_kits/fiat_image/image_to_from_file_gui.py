from fiatlight.fiat_types.file_types import ImagePath, ImagePath_Save
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from imgui_bundle import imgui, portable_file_dialogs as pfd
from .image_types import ImageU8_3


_ACCEPT_ANY_FILE = "*.*"


def image_from_file(path: ImagePath, convert_bgr_to_rgb: bool = False) -> ImageU8_3 | None:
    """Read an image from a file.
    Note: This function uses OpenCV to read the image. By default, OpenCV reads images in BGR format.
    If you want to convert the image to RGB format, set the `convert_bgr_to_rgb` parameter to `True`.
    """
    import cv2  # noqa

    try:
        img = cv2.imread(path)
        if convert_bgr_to_rgb:
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif len(img.shape) == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        return img  # type: ignore
    except Exception:
        return None


class ImageToFileGui(FunctionWithGui):
    _save_dialog: pfd.save_file | None = None
    _image: ImageU8_3 | None = None
    _exception_message: str | None = None

    def __init__(self) -> None:
        super().__init__(self.f, "ImageToFile")
        self.internal_state_gui = self._internal_state_gui

    def f(self, image: ImageU8_3, convert_rgb_to_bgr: bool = False) -> None:
        import cv2

        self._image = image
        if convert_rgb_to_bgr:
            if len(image.shape) == 3:
                self._image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # type: ignore
            elif len(image.shape) == 4:
                self._image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)  # type: ignore

    def do_write(self, path: ImagePath_Save) -> None:
        import cv2

        assert self._image is not None
        try:
            cv2.imwrite(path, self._image)
        except Exception:
            self._exception_message = f"Failed to write image to file {path}"

    def _internal_state_gui(self) -> bool:
        if self._image is None:
            return False
        if imgui.button("Save file"):
            self._save_dialog = pfd.save_file("Select file", "", ["*.txt", _ACCEPT_ANY_FILE])
        if self._save_dialog is not None and self._save_dialog.ready():
            selected_file = self._save_dialog.result()
            self.do_write(selected_file)  # type: ignore
            self._save_dialog = None
        if self._exception_message is not None:
            from fiatlight import fiat_config as fc

            color = fc.get_fiat_config().style.color_as_vec4(fc.FiatColorType.ExceptionError)
            imgui.text_colored(color, self._exception_message)
            return False
        return False
