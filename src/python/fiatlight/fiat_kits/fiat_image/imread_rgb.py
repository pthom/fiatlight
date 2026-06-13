"""Read an image file as a numpy array in RGB(A) order.

Uses OpenCV when available, otherwise falls back to Pillow, so image I/O works
without a heavyweight opencv install (load + display + your own numpy code).
"""

from .image_types import ImageU8
import numpy as np


def imread_rgb(image_file: str) -> ImageU8:
    """Read an image file and return a numpy array in RGB (or RGBA) order.

    Tries OpenCV first, then Pillow; raises ImportError if neither is installed.
    """
    try:
        import cv2
    except ImportError:
        return _imread_rgb_pillow(image_file)

    img = cv2.imread(image_file)
    assert img is not None
    if len(img.shape) == 3:
        nb_channels = img.shape[2]
        if nb_channels == 4:
            img = np.ascontiguousarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA))
        elif nb_channels == 3:
            img = np.ascontiguousarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return img  # type: ignore


def _imread_rgb_pillow(image_file: str) -> ImageU8:
    try:
        from PIL import Image
    except ImportError as e:
        raise ImportError(
            "Reading images requires either opencv-python or Pillow. " "Install one of them, e.g. `pip install Pillow`."
        ) from e

    pil_image = Image.open(image_file)
    # Preserve alpha when present, else RGB — matching the OpenCV path's contract.
    mode = "RGBA" if "A" in pil_image.getbands() else "RGB"
    # np.array (not np.asarray): PIL exposes a read-only buffer, and immvision /
    # downstream code needs a writable, contiguous array.
    return np.array(pil_image.convert(mode))  # type: ignore
