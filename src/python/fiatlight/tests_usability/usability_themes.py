import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import image_from_file
from fiatlight.fiat_kits.fiat_image.cv2_nodes import Canny, dilate

fl.run([image_from_file, Canny, dilate], app_name="demo_computer_vision")
