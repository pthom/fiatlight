import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import image_from_file, lut_channels_in_colorspace
from fiatlight.fiat_kits.fiat_image import lut_types


def demo_lut_channels_in_colorspace() -> None:
    fl.run([image_from_file, lut_channels_in_colorspace], app_name="lut_gui_demo")


def demo_lut_types() -> None:
    def f(color_lut_params: lut_types.ColorLutParams) -> str:
        return str(color_lut_params)

    fl.run(f, app_name="lut_gui_demo")


demo_lut_types()
