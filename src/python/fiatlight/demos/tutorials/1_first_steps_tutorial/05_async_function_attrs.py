"""Using async functions for long processing times

Let's see how fiatlight can handle functions which take more time to execute.
First, we will add a delay in the "detect edges" function, to simulate a long processing time.

Then using the command line "fiatlight fn attrs" we can see that "invoke async" enables to run
the function in a separate thread, so that the GUI remains responsive.
We may also set "invoke manually" to avoid running the function automatically when an input changes
(this is completely up to you, depending on your use case).

So, we will add these two attributes to our "detect edges" function: "invoke async" and "invoke manually".

Then, we can see that our GUI is updated with our customizations:
as soon as we change a parameter, the function is not invoked automatically,
instead we have to click on a button near the label "Refresh needed" to invoke the function.

While the function is running, the user interface remains responsive,
and you can see a spinning icon in the top right corner of the node.


"""

import cv2
import time
import fiatlight as fl

# ImagePath is a synonym for str, which will be presented in the GUI as a file selector
from fiatlight.fiat_types import ImagePath

#  ImageRgb is a synonym for a numpy array, which will be presented in the GUI with an image analyzer
from fiatlight.fiat_kits.fiat_image import ImageRgb


@fl.with_fiat_attributes(label="Read Image from File")
def read_image(image_path: ImagePath) -> ImageRgb:
    """Reads an image from a file and returns it as an ImageRgb (i.e. a numpy array in RGB order)"""
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV uses BGR by default
    return img


def detect_edges(image: ImageRgb, low_threshold: float = 100.0, high_threshold: float = 200.0) -> ImageRgb:
    """Detects edges in an image and returns a new image with the edges"""
    time.sleep(3)  # Simulate a long processing time
    return cv2.Canny(image, low_threshold, high_threshold)


# Customize the GUI for the detect_edges function, by adding fiat attributes
fl.add_fiat_attributes(
    detect_edges,
    invoke_async=True,  # Run the function in a separate thread
    invoke_manually=True,  # Add a play button to invoke the function manually
    label="Canny Edge Detector",  # Set a custom label for the function node
    low_threshold__label="Low Threshold",  # Set a custom label for the low_threshold parameter
    low_threshold__tooltip="Lower threshold for the Canny edge detector",
    low_threshold__edit_type="slider",  # Use a slider to edit the low_threshold parameter
    low_threshold__range=(0, 5000),  # Set the range of the slider
    low_threshold__slider_logarithmic=True,  # Use a logarithmic scale for the slider
    high_threshold__edit_type="slider",
    high_threshold__label="High Threshold",
    high_threshold__tooltip="Upper threshold for the Canny edge detector",
    high_threshold__range=(0, 5000),
    high_threshold__slider_logarithmic=True,
)


fl.run([read_image, detect_edges])
