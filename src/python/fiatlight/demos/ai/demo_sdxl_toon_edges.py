import fiatlight as fl
from fiatlight.fiat_kits.fiat_ai import invoke_sdxl_turbo
from fiatlight.demos.images.toon_edges import add_toon_edges
from fiatlight.fiat_kits.fiat_image import lut_channels_in_colorspace


def main() -> None:
    fl.run([invoke_sdxl_turbo, lut_channels_in_colorspace, add_toon_edges], app_name="demo_sdxl_toon_edges")


if __name__ == "__main__":
    main()
