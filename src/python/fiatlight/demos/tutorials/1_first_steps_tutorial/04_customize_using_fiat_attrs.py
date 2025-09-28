"""Customize the GUI using fiat attributes

Here, we continue from the previous image example.

Going back to the fiatlight command line interface, we can see that we can get info on how to customize the GUI for float parameters, by typing: "fiatlight gui float"
There, we can see customization options such as "range", "edit_type", "slider_logarithmic", "label", "tooltip", etc.

We will use some of these options to customize the GUI for the "detect edges" function:

For this, we will use the "fiatlight add_fiat_attributes" function which enables us to add customizations to the GUI for an existing function. To customize the GUI for a function parameter, we use the following naming convention: parameter_name followed by two underscores, followed by the attribute name.
Here, we will customize the "low_threshold" and "high_threshold" parameters of the "detect_edges" function.

Then, going back to the fiatlight command line interface, we can see that we can get info on how to customize the GUI at a function level, by typing: "fiatlight fn attrs".
There, we can see customization options such as "label", "invoke async", etc.
Let's add a label to our function, by simply adding "label" as an argument to "add_fiat_attributes".

Let's now add a label to the "read image" function.
This time, instead of using "add fiat attributes", we will use the decorator named "with fiat attributes" to add the label directly to the function definition. This is shorter, but more intrusive as it modifies the function definition itself.

Then, we can see that our GUI is updated with our customizations: the function is now labeled "Canny Edge Detector", and the two thresholds are now sliders with logarithmic scale and a range from 0 to 5000.

Let's see how fiatlight can handle functions which take more time to execute.
First, we will add a delay in the "detect edges" function, to simulate a long processing time.

"""

import cv2

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
    return cv2.Canny(image, low_threshold, high_threshold)


# Customize the GUI for the detect_edges function, by adding fiat attributes
fl.add_fiat_attributes(
    detect_edges,
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


# app_name will set the window title, as well as the name of the saved settings file
fl.run([read_image, detect_edges], app_name="Your app name here")
