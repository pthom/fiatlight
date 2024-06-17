import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import image_from_file
from fiatlight.demos.images.opencv_wrappers import canny, dilate

fl.run([image_from_file, canny, dilate], app_name="demo_computer_vision")
