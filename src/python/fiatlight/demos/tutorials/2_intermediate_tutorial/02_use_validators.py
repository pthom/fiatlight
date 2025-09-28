"""Use validators to check function parameters

Let's see how to use validators to check function parameters.

We continue from the previous image example.
We added an integer aperture_size parameter to the Canny edge detector function.
However, the OpenCV documentation specifies that the only valid values for this parameter are 3, 5, and 7.

In this part, we will solve this problem by writing a validator function for this parameter.
A validator function behaves like a pydantic validator i.e. :
    - it receives the current value
    - it raises a ValueError if the value is not valid
    - it returns a possibly modified value

Here, we will implement two possible behaviors:
- Option 1: raise a ValueError if the value is not valid
- Option 2: return a possibly modified value, using the closest valid value

Then, we will register this validator function for the aperture_size parameter using fiatlight's add_fiat_attributes function.

When running the app, we can see that if we enter an invalid value (for example 4), either:

- we get a clear error message indicating that the value is not valid (if using Option 1)
- or the value is automatically changed to the closest valid value (if using Option 2)
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


# We write a validator function for the aperture_size parameter
# It behaves like a pydantic validator i.e. :
#   - it receives the current value
#   - it raises a ValueError if the value is not valid
#   - it returns a possibly modified value
def validate_aperture_size(aperture_size: int) -> int:
    # Option 1: raise a ValueError if the value is not valid
    # valid_values = [3, 5, 7]
    # if aperture_size not in valid_values:
    #     raise ValueError(f"Invalid aperture_size: {aperture_size}. Valid values are {valid_values}")
    # return aperture_size

    # Option 2: return a possibly modified value, using the closest valid value
    valid_values = [3, 5, 7]
    if aperture_size not in valid_values:
        closest_value = min(valid_values, key=lambda x: abs(x - aperture_size))
        return closest_value
    else:
        return aperture_size


fl.add_fiat_attributes(
    detect_edges,
    aperture_size__range=(3, 7),  # Set the range of the slider
    aperture_size__edit_type="slider",  # Use a slider to edit the aperture_size parameter
    aperture_size__validator=validate_aperture_size,  # Set the validator for the aperture_size parameter
)


fl.run([read_image, detect_edges])
