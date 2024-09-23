"""fiat_image kit demo:
In this example, a first node enables to load an image from the filesystem
Three nodes are then connected to the first one:
- The first node detects edges in the image using the Canny algorithm
- The second node computes the Sobel operator on the image in the horizontal or vertical direction
- The third node applies a LUT to the image in the HSL colorspace

The image viewer, provided by fiat_kits.fiat_image, is used to display the results of in the 4 nodes.
Thanks to this advanced viewer:
- The images can be zoomed in synchronously
- They can also be panned synchronously
- The pixel values under the mouse cursor are displayed below the image
- When the zoom level is sufficiently high, the pixel values are displayed on the image.
  For float images, like the output of the Sobel operator, the values are displayed as a float.
- Float image can be displayed using a colormap
- Any image that is displayed can be saved to the filesystem.
  It can also be transferred to an image inspector, for further analysis.
"""

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import lut_channels_in_colorspace
from fiatlight.fiat_kits.fiat_image import image_source, ImageU8_3, ImageFloat
from fiatlight.demos.images.opencv_wrappers import canny
from enum import Enum
import cv2


class Orientation(Enum):
    """Orientation of the Sobel operator: horizontal or vertical."""

    Horizontal = 0
    Vertical = 1


def compute_sobel(image: ImageU8_3, orientation: Orientation) -> ImageFloat:
    """Compute the Sobel operator on an image, i.e. the gradient of the image in the x or y direction"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_float = gray / 255.0
    blur_size = 3
    blurred = cv2.GaussianBlur(img_float, (0, 0), sigmaX=blur_size, sigmaY=blur_size)
    dx, dy = (1, 0) if orientation == Orientation.Horizontal else (0, 1)
    r = cv2.Sobel(blurred, ddepth=cv2.CV_64F, dx=dx, dy=dy, ksize=3, scale=1.0)
    return r  # type: ignore


def main() -> None:
    graph = fl.FunctionsGraph()
    graph.add_function(image_source)

    graph.add_function(canny)
    graph.add_link(image_source, canny)

    graph.add_function(compute_sobel)
    graph.add_link(image_source, compute_sobel)

    graph.add_function(lut_channels_in_colorspace)
    graph.add_link(image_source, lut_channels_in_colorspace)

    fl.run(graph, app_name="demo_computer_vision", params=fl.FiatRunParams(delete_settings=False))


if __name__ == "__main__":
    main()
