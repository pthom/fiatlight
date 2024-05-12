"""Given a snippet of code, run the corresponding application and save a screenshot. """
from fiatlight.fiat_runner.fiat_shot_snippet import add_screenshots_to_markdown_file

snippet = """
import math
import fiatlight

def my_asin(x: float = 0.5) -> float:
    return x * 2


fiatlight.fiat_run(my_asin)
"""


add_screenshots_to_markdown_file(
    "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/src/python/fiatlight/doc/customize_params_gui.md"
)
