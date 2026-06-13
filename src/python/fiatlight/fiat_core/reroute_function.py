"""Reroute (relay) node: a polymorphic passthrough used to tidy crossing wires.

A reroute has one input and one output and forwards its value unchanged. Its pin
type is polymorphic ("adopt on connect"): it starts as `Any` (so it accepts a link
from any output), and once its input is connected it adopts the source's concrete
type, so links *downstream* of the reroute are still type-checked.

The adoption is driven centrally by `FunctionsGraph._recompute_reroute_types` (which
also enforces that adopting a type never silently breaks an existing downstream link),
not from here. This module only defines the node and how to set its pin type.
"""
import typing
from typing import Any

from fiatlight.fiat_core.function_with_gui import FunctionWithGui

# Single input param name (matches `_reroute_identity`'s parameter).
REROUTE_INPUT_NAME = "value"


def _reroute_identity(value):  # type: ignore[no-untyped-def]  # pins are (re)typed via set_pin_type, not from annotations
    return value


class RerouteFunctionWithGui(FunctionWithGui):
    """Passthrough node whose single pin type adopts the type flowing into it."""

    def __init__(self) -> None:
        super().__init__(_reroute_identity, fn_name="Reroute")
        self.set_pin_type(typing.Any)

    def set_pin_type(self, type_: Any) -> None:
        """Set both the input and output pin type. `typing.Any` makes the reroute
        accept a link from/to any pin (see `fiat_types.type_compat`). Called by the
        graph's reroute-type recomputation; not meant to be called directly."""
        self.input(REROUTE_INPUT_NAME)._type = type_
        self.output(0)._type = type_


def is_reroute(function_with_gui: FunctionWithGui) -> bool:
    return isinstance(function_with_gui, RerouteFunctionWithGui)
