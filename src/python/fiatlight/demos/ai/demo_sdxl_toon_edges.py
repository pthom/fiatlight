import fiatlight
from fiatlight.demos.ai.stable_diffusion_xl_wrapper import invoke_stable_diffusion_xl
from fiatlight.demos.images.toon_edges import add_toon_edges
from fiatlight.fiat_kits.fiat_image import lut_channels_in_colorspace


def main() -> None:
    fiatlight.fiat_run_composition([invoke_stable_diffusion_xl, lut_channels_in_colorspace, add_toon_edges])


if __name__ == "__main__":
    main()
