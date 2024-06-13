"""Demo how to set custom presentation attributes for the Image Widget (ImageWithGui)

Notes:
    - Documentation: fl.fiat_kits.fiat_image.image_custom_attributes_documentation()
      will return a full documentation of the custom attributes.
    - The custom attributes can be set using the decorator fl.with_custom_attrs
    - In these examples, we intend to set custom attributes for the output of the
      functions, i.e. the returned value.
      As a consequence, the custom attributes are set in the return__...
      arguments of the decorator.
"""

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8_3
import cv2


# Our demo image
demo_image: ImageU8_3 = cv2.imread(fl.demo_assets_dir() + "/images/house.jpg")  # type: ignore


# A simple function that will use the Image Widget with its default settings.
def show_image(image: ImageU8_3 = demo_image) -> ImageU8_3:
    return image


# A function whose output will initially show the channels
# Since it does not specify a zoom key,
# it will be zoomed and panned together with the image
# shown by "show_image"
@fl.with_fiat_attributes(return__show_channels=True)
def show_image_channels(image: ImageU8_3 = demo_image) -> ImageU8_3:
    return image


# A function whose output will have a different zoom key:
# it can be panned and zoomed, independently of the other images
@fl.with_fiat_attributes(return__zoom_key="other")
def show_image_different_zoom_key(image: ImageU8_3 = demo_image) -> ImageU8_3:
    return image


# A function that will use the Image Widget with custom attributes:
# - the image is displayed only (it cannot be zoomed or panned,
#   and the pixel values are not shown)
# - the image is displayed with a height of 300 pixels
#   (the width is automatically calculated)
# - the image cannot be resized
@fl.with_fiat_attributes(
    return__only_display=True,
    return__image_display_size=(0, 300),
    return__can_resize=False,
)
def show_image_only_display(image: ImageU8_3 = demo_image) -> ImageU8_3:
    return image


def main() -> None:
    graph = fl.FunctionsGraph()
    graph.add_function(show_image)
    graph.add_function(show_image_channels)
    graph.add_function(show_image_different_zoom_key)
    graph.add_function(show_image_only_display)

    fl.run(graph, app_name="fiat_image_custom_attrs_demo")


if __name__ == "__main__":
    main()
