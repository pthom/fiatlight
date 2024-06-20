from fiatlight.fiat_kits import fiat_image as fi
from fiatlight.fiat_kits.fiat_image.image_processors import apply_image_effect
import fiatlight as fl


def main() -> None:
    camera_gui = fi.CameraImageProviderGui()
    image_to_file = fi.ImageToFileGui()
    fl.run([camera_gui, apply_image_effect, image_to_file])


if __name__ == "__main__":
    main()
