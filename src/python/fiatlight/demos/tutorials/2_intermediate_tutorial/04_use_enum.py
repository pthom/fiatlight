"""Use an enum-like widget for a function parameter.

We continue from the previous image example.
We added an integer aperture_size parameter to the Canny edge detector function.
However, the OpenCV documentation specifies that the only valid values for this parameter are 3, 5, and 7.

In this part, we will solve this problem by using an Enum type for this parameter.

The solution is very simple:
we define an Enum class with the valid values, and we use this Enum class as the type of the parameter.

And we can see that the generated GUI works perfectly!

"""
import cv2
from enum import Enum
import fiatlight as fl
from fiatlight.fiat_types import ImagePath
from fiatlight.fiat_kits.fiat_image import ImageRgb


@fl.with_fiat_attributes(label="Read Image from File")
def read_image(image_path: ImagePath) -> ImageRgb:
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


class ApertureSizeEnum(Enum):
    size_3 = 3
    size_5 = 5
    size_7 = 7


def detect_edges(
    image: ImageRgb,
    low_threshold: float = 100.0,
    high_threshold: float = 200.0,
    aperture_size: ApertureSizeEnum = ApertureSizeEnum.size_3,
) -> ImageRgb:
    """Detects edges in an image and returns a new image with the edges
    Following OpenCV documentation, the only valid values for aperture_size are 3, 5, and 7.
    """
    return cv2.Canny(image, low_threshold, high_threshold, apertureSize=aperture_size.value)


# Run the app with our two functions (using the customized detect_edges_gui)
fl.run([read_image, detect_edges], app_name="Your app name here")
