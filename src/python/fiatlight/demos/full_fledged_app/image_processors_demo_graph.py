"""An example with you can display a camera, apply a variety of image effects onto it, and save the result to a file.

This is an example usage of image_processors, inside a function graph provided by Fiatlight.

It also shows how a simple pipeline can be built, going from a source (here a camera image) to a sink (here a file).
"""

from fiatlight.fiat_kits import fiat_image as fi
from fiatlight.fiat_kits.fiat_image.image_processors import apply_image_effect
import fiatlight as fl


def main() -> None:
    camera_gui = fi.CameraImageProviderGui()
    image_to_file = fi.ImageToFileGui()
    fl.run([camera_gui, apply_image_effect, image_to_file])


if __name__ == "__main__":
    main()
