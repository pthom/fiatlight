import fiatlight
from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo
from fiatlight.demos.images.toon_edges import add_toon_edges
from fiatlight.fiat_kits.fiat_image import lut_channels_in_colorspace


def main() -> None:
    fiatlight.fiat_run_composition([invoke_sdxl_turbo, lut_channels_in_colorspace, add_toon_edges])


if __name__ == "__main__":
    main()
