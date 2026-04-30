"""Visual smoke for `RoiPicker`.

Pipeline: image_source -> select_roi -> (rect goes nowhere yet, just
inspect the output pin's interactive widget).
"""
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import RoiPicker, image_source


picker = RoiPicker()
picker_node = picker.bind()

graph = fl.FunctionsGraph()
graph.add_function(image_source)
graph.add_function(picker_node)
graph.add_link("image_source", "select_roi", "image")
fl.run(graph)
