"""reads an image file and returns a numpy array with the image data in RGB order, using OpenCV"""

import cv2
from .image_types import ImageU8
import numpy as np


def imread_rgb(image_file: str) -> ImageU8:
    """reads an image file and returns a numpy array with the image data in RGB order, using OpenCV"""
    img = cv2.imread(image_file)
    if len(img.shape) == 3:
        nb_channels = img.shape[2]
        if nb_channels == 4:
            img = np.ascontiguousarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA))
        elif nb_channels == 3:
            img = np.ascontiguousarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return img  # type: ignore
