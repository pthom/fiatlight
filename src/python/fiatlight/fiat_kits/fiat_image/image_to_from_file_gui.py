from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes
from fiatlight.fiat_types.file_types import ImagePath, ImagePath_Save
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from imgui_bundle import imgui, portable_file_dialogs as pfd
from .image_types import ImageU8


_ACCEPT_ANY_FILE = "*.*"


@with_fiat_attributes(
    path__label="File",
    label="Image from file",
    fiat_tags=["source"],
)
def image_from_file(path: ImagePath) -> ImageU8:
    """Read an image from a file.
    Note: This function uses OpenCV to read the image, but it makes sure to return the image in RGB order.
    """
    from fiatlight.fiat_kits.fiat_image.imread_rgb import imread_rgb

    img = imread_rgb(path)
    return img


@with_fiat_attributes(
    path__label="File",
    max_image_size__range=(1, 3000),
    max_image_size__label="Max Image Size",
    max_image_size__tooltip="If the image with or height is larger than this size, it will be resized",
    label="Image from file (resized)",
    fiat_tags=["source"],
)
def image_from_file_resized(path: ImagePath, max_image_size: int | None = None) -> ImageU8:
    """A simple function that reads an image from a file and optionally resizes it if it is too large."""
    from fiatlight.fiat_kits.fiat_image.imread_rgb import imread_rgb

    image = imread_rgb(path)

    if max_image_size is not None:
        try:
            import cv2
        except ImportError:
            raise ImportError("cv2 is required to resize the image, please install it with 'pip install opencv-python'")
        if image.shape[0] > max_image_size or image.shape[1] > max_image_size:
            k = max_image_size / max(image.shape[0], image.shape[1])
            assert k > 0.0
            image = cv2.resize(image, None, fx=k, fy=k)  # type: ignore
    return image


class ImageToFileGui(FunctionWithGui):
    _save_dialog: pfd.save_file | None = None
    _image: ImageU8 | None = None
    _exception_message: str | None = None

    def __init__(self) -> None:
        super().__init__(self.f, "ImageToFile")
        self.internal_state_gui = self._internal_state_gui

    def f(self, image: ImageU8) -> None:
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
