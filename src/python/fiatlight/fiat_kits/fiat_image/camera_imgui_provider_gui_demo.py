import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import CameraImageProviderGui


cam = CameraImageProviderGui()
fl.run(cam, app_name="camera_imgui_provider_gui_demo")
