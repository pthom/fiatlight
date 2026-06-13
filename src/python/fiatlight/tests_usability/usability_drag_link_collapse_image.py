"""Usability: a freshly-linked image input should show only its one-line
presentation, not a redundant full-image render (the image is already visible
on the upstream output pane).

To exercise it:
  1. Drag a wire FROM the `image_from_file` output pin onto empty canvas, then
     pick `canny` (or `dilate`) in the palette. The new node's image input pin
     should be COLLAPSED (one line: "Image (...) ...") rather than rendering the
     full image again.
  2. Same when manually dragging a link between two existing image pins.
Click the input's expand button to render it fully if wanted.
"""

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import image_from_file
from fiatlight.fiat_kits.fiat_image.cv2_nodes import Canny, dilate

fl.run_graph_composer([image_from_file, Canny, dilate], app_name="usability_drag_link_collapse_image")
