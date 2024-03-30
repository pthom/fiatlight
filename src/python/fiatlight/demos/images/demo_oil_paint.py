from fiatlight import fiat_run_composition
from fiatlight.fiat_image import lut_channels_in_colorspace
from fiatlight.fiat_image import image_source
from fiatlight.demos.images.opencv_wrappers import oil_paint


def main() -> None:
    fiat_run_composition([image_source, lut_channels_in_colorspace, oil_paint])


if __name__ == "__main__":
    main()
