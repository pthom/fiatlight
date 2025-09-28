"""Handle exceptions when calling functions

Let's see how to handle exceptions when calling functions.

In this example, we continue from the previous image example.
We added an integer aperture_size parameter to the Canny edge detector function.

However, the OpenCV documentation specifies that the only valid values for this parameter are 3, 5, and 7.

Thus, if we run our app as is, the user could enter any integer value, which can lead to an error at runtime, for example if the user enters 4.

As you can see, Fiatlight is able to catch this error, and to display the exception in the user interface.Fiatlight even provides a button to "Debug this exception": let's click on it.

The exception is replayed, and we see that the call to cv2.Canny fails because the aperture_size is invalid.

This is a very nice way to replay errors "post-mortem", and to debug them.
"""
import cv2
import fiatlight as fl
from fiatlight.fiat_types import ImagePath
from fiatlight.fiat_kits.fiat_image import ImageRgb


def read_image(image_path: ImagePath) -> ImageRgb:
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def detect_edges(
    image: ImageRgb,
    low_threshold: float = 100.0,
    high_threshold: float = 200.0,
    aperture_size: int = 3,  # Valid values are (3, 5, 7) !
) -> ImageRgb:
    """Detects edges in an image and returns a new image with the edges
    Following OpenCV documentation, the only valid values for aperture_size are 3, 5, and 7.
    """
    return cv2.Canny(image, low_threshold, high_threshold, apertureSize=aperture_size)


fl.run([read_image, detect_edges])
