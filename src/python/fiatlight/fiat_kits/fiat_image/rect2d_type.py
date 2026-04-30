"""Single 2D axis-aligned rectangle as a Pydantic model.

Mirror of `Point2D` for the per-rectangle case. Used as an input pin
(e.g. ROI selector output) and gets a free auto-generated 4-int edit
form when used outside the interactive picker context.
"""

from pydantic import BaseModel

from fiatlight.fiat_togui.gui_registry import base_model_with_gui_registration


@base_model_with_gui_registration()
class Rect2D(BaseModel):
    """A single axis-aligned rectangle (integer x, y, w, h)."""

    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0
