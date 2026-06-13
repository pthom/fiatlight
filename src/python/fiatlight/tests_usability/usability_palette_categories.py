"""Usability: palette categories (issue #4).

Mixes three domains so the palette shows a Category selector (image / text /
math). Selecting a category scopes the tag chips below it. The category selector
is hidden when there is only one category, so this script deliberately spans
several.

Check:
  - A "Category:" row with [All] [image] [math] [text].
  - Selecting `image` shows only image tags (incl. `cv2`); selecting `text`
    shows only `string` etc.
  - The doc panel shows `Category:` and `Tags:`.
"""

from typing import Any, Callable

import fiatlight as fl
from fiatlight.fiat_kits.fiat_image.cv2_nodes import Canny, GaussianBlur


@fl.with_fiat_attributes(fiat_tags=["string"], fiat_category="text")
def to_upper(text: str = "hello") -> str:
    return text.upper()


@fl.with_fiat_attributes(fiat_tags=["string"], fiat_category="text")
def repeat(text: str = "ab", times: int = 3) -> str:
    return text * times


@fl.with_fiat_attributes(fiat_tags=["arithmetic"], fiat_category="math")
def add(a: int = 1, b: int = 2) -> int:
    return a + b


@fl.with_fiat_attributes(fiat_tags=["arithmetic"], fiat_category="math")
def int_entry(x: int = 0) -> int:
    return x


@fl.with_fiat_attributes(fiat_tags=["arithmetic"], fiat_category="math")
def multiply(a: int = 2, b: int = 3) -> int:
    return a * b


available_functions: list[Callable[..., Any]] = [Canny, GaussianBlur, to_upper, repeat, int_entry, add, multiply]


# Add synthetic functions to the palette to test many tags
for i in range(10):

    @fl.with_fiat_attributes(fiat_tags=[f"tag{i}"], fiat_category="math")
    def synthetic_function(x: int = 0) -> int:
        return x + i

    available_functions.append(synthetic_function)


# Canny / GaussianBlur are category "image" (set by the cv2_nodes kit defaults).
fl.run_graph_composer(available_functions, app_name="usability_palette_categories")
