"""Compose image processing functions with fiatlight.
In this example, we will compose two simple image processing functions: "read image" which reads an image from a file,
and "detect edges" which detects edges in the image using the Canny algorithm.

Note that we are using two types from fiatlight: ImagePath, and ImageRgb which are synonyms for str and numpy array respectively.
ImagePath will be presented in the GUI as a file selector, and ImageRgb will be presented with a widget to display the image.

Then we use fl.run() to run the application, passing the two functions as a list:
the output of the first function will be passed as input to the second function (for its first parameter).

====

When we run the application, we get a GUI with two nodes: "read image" and "detect edges".
We can see that the output of the first node is connected to the input of the second node.

We can select an image file in the first node: we click on the "+", then on "Select File".

After we selected our image, we can see it in the first node's output,
and the edges detected in the second node's output.

You can then adjust the parameters of the "detect edges" node to see how it affects the output.

These images widgets can be resized, zoomed and panned, in a synchronized way.
With high zoom, you can see the pixel values.
You can also save the images, or send them to an "inspector" tab for further analysis.


"""
import cv2

import fiatlight as fl

# ImagePath is a synonym for str, which will be presented in the GUI as a file selector
from fiatlight.fiat_types import ImagePath

#  ImageRgb is a synonym for a numpy array, which will be presented in the GUI with an image analyzer
from fiatlight.fiat_kits.fiat_image import ImageRgb


def read_image(image_path: ImagePath) -> ImageRgb:
    """Reads an image from a file and returns it as an ImageRgb (i.e. a numpy array in RGB order)"""
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV uses BGR by default
    return img


def detect_edges(image: ImageRgb, low_threshold: int = 100, high_threshold: int = 200) -> ImageRgb:
    """Detects edges in an image and returns a new image with the edges"""
    return cv2.Canny(image, low_threshold, high_threshold)


fl.run([read_image, detect_edges])
