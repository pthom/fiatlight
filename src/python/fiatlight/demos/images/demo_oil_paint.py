from fiatlight import run
from fiatlight.fiat_kits.fiat_image import lut_channels_in_colorspace
from fiatlight.fiat_kits.fiat_image import image_source  # noqa
from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo  # noqa
from fiatlight.demos.images.opencv_wrappers import oil_paint
from fiatlight.demos.images.old_school_meme import add_meme_text


def main() -> None:
    source = image_source
    # source = invoke_sdxl_turbo
    run([source, lut_channels_in_colorspace, oil_paint, add_meme_text])


if __name__ == "__main__":
    main()
