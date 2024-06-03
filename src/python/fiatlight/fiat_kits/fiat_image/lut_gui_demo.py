import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import image_from_file, lut_channels_in_colorspace

fl.run([image_from_file, lut_channels_in_colorspace], app_name="lut_gui_demo")
