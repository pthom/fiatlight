"""Usability: the redesigned "any range" float slider.

Each source starts at a different magnitude so you can check the inferred range:
  - zero        -> range 0–1
  - wide value  -> range grows to 1e8, log auto-on
  - negative    -> symmetric range, ± on

Try: ÷10 / x10 to rescale the range, `log` toggle, `±` toggle (symmetric range
for negatives), and Ctrl/double-click the slider to type an exact value
(e.g. 4.016e7 grows the range to fit).
"""

import fiatlight as fl


@fl.with_fiat_attributes(x__edit_type="slider_float_any_range")
def from_zero(x: float = 0.0) -> float:
    return x


@fl.with_fiat_attributes(x__edit_type="slider_float_any_range")
def from_wide(x: float = 4.016e7) -> float:
    return x


@fl.with_fiat_attributes(x__edit_type="slider_float_any_range")
def from_negative(x: float = -3.5) -> float:
    return x


@fl.with_fiat_attributes(x__edit_type="slider_float_any_range_positive")
def positive_only(x: float = 0.0) -> float:
    return x


graph = fl.FunctionsGraph()
graph.add_function(from_zero)
graph.add_function(from_wide)
graph.add_function(from_negative)
graph.add_function(positive_only)
fl.run(graph, app_name="usability_float_source")
