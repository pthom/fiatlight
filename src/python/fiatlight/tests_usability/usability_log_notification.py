"""Usability: exceptions raised by a function should NOT auto-open the Log
window. Instead:
  - a transient notification appears in the bottom-right corner (showing the
    log message),
  - the status bar shows an orange "N new log message(s)" indicator with an
    "Open Log" button.

To exercise it: set `denominator` to 0 (raises), or type into `text` a value
that triggers the warning. Then check the bottom-right notification + the
status bar indicator, and click "Open Log".
"""

import logging
import fiatlight as fl


@fl.with_fiat_attributes(label="Divide (raises on 0)")
def divide(numerator: int = 10, denominator: int = 2) -> float:
    # Raises ZeroDivisionError when denominator == 0: the exception is caught by
    # fiatlight, logged, and surfaced via notification + status bar.
    return numerator / denominator


@fl.with_fiat_attributes(label="Warn if negative")
def warn_if_negative(value: int = 1) -> int:
    if value < 0:
        logging.warning(f"warn_if_negative received a negative value: {value}")
    return value


graph = fl.FunctionsGraph()
graph.add_function(divide)
graph.add_function(warn_if_negative)
fl.run(graph)
