"""A simple pipeline where you can load an image, apply a LUT to it (change the colors), and then save it.
Demonstrates how to use the `image_from_file` and `ImageToFileGui` functions.
"""

from fiatlight.fiat_kits.fiat_image import image_from_file, lut_channels_in_colorspace, ImageToFileGui
import fiatlight


def main() -> None:
    fiatlight.run([image_from_file, lut_channels_in_colorspace, ImageToFileGui()])
    # fiatlight.run([image_from_file])


if __name__ == "__main__":
    main()
