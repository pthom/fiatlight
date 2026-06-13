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
from fiatlight.fiat_types.base_types import JsonDict

# Single input param name (matches `_reroute_identity`'s parameter).
REROUTE_INPUT_NAME = "value"


def _reroute_identity(value):  # type: ignore[no-untyped-def]  # pins are (re)typed via set_pin_type, not from annotations
    return value


class RerouteFunctionWithGui(FunctionWithGui):
    """Passthrough node whose single pin type adopts the type flowing into it.

    Rendered as a minimal node (just the two pins, no title/widgets — see
    `FunctionNodeGui`). `rotation` (quarter-turns, 0..3: 0 = input-left/output-right,
    then clockwise) and `show_type` are display-only options, toggled from the
    node's context menu and persisted in the workspace."""

    def __init__(self) -> None:
        super().__init__(_reroute_identity, fn_name="Reroute")
        self.set_pin_type(typing.Any)
        self.rotation: int = 0  # quarter-turns clockwise (0..3)
        self.show_type: bool = False
        self.save_internal_gui_options_to_json = self._save_display_options
        self.load_internal_gui_options_from_json = self._load_display_options

    def rotate(self, quarter_turns: int) -> None:
        self.rotation = (self.rotation + quarter_turns) % 4

    def set_pin_type(self, type_: Any) -> None:
        """Set both the input and output pin type. `typing.Any` makes the reroute
        accept a link from/to any pin (see `fiat_types.type_compat`). Called by the
        graph's reroute-type recomputation; not meant to be called directly."""
        self.input(REROUTE_INPUT_NAME)._type = type_
        self.output(0)._type = type_

    def _save_display_options(self) -> JsonDict:
        return {"rotation": self.rotation, "show_type": self.show_type}

    def _load_display_options(self, data: JsonDict) -> None:
        rotation = data.get("rotation", 0)
        if isinstance(rotation, int):
            self.rotation = rotation % 4
        self.show_type = bool(data.get("show_type", False))


def is_reroute(function_with_gui: FunctionWithGui) -> bool:
    return isinstance(function_with_gui, RerouteFunctionWithGui)
