from fiatlight.fiat_types.file_types import ImagePath, ImagePath_Save
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from imgui_bundle import imgui, portable_file_dialogs as pfd
from .image_types import ImageRgb


_ACCEPT_ANY_FILE = "*.*"


def image_from_file(path: ImagePath) -> ImageRgb | None:
    """Read an image from a file.
    Note: This function uses OpenCV to read the image, but it makes sure to return the image in RGB order.
    """
    from fiatlight.fiat_kits.fiat_image.imread_rgb import imread_rgb

    try:
        img = imread_rgb(path)
        return img  # type: ignore
    except Exception:
        return None


class ImageToFileGui(FunctionWithGui):
    _save_dialog: pfd.save_file | None = None
    _image: ImageRgb | None = None
    _exception_message: str | None = None

    def __init__(self) -> None:
        super().__init__(self.f, "ImageToFile")
        self.internal_state_gui = self._internal_state_gui

    def f(self, image: ImageRgb) -> None:
        self._image = image

    def do_write(self, path: ImagePath_Save) -> None:
        import cv2

        assert self._image is not None
        try:
            img_bgr = cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(path, img_bgr)
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
