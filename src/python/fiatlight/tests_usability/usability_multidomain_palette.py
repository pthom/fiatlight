"""Usability: a multi-domain palette (issue #4 payoff).

Loads the cv2 image pack + the math pack + the text pack, so the palette's
Category selector shows image / math / text, each populated with real nodes,
and the tag chips scope to the selected category.

Try:
  - Switch Category between image / math / text and watch the tag chips change.
  - Build a cross-domain pipeline, e.g.
    text_source -> split_words -> count_words (text)  ->  ... feeding math nodes.
"""

from fiatlight.fiat_kits.fiat_image.cv2_nodes import cv2_nodes
from fiatlight.fiat_kits.fiat_math import math_nodes
from fiatlight.fiat_kits.fiat_text import text_nodes

import fiatlight as fl

fl.run_graph_composer(
    functions=[*cv2_nodes(), *math_nodes(), *text_nodes()],
    app_name="usability_multidomain_palette",
)
