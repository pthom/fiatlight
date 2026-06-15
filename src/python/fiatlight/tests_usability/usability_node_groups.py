"""Manual smoke test for classic groups (tinted rectangles behind the nodes).

Run it, then exercise each entry point:

1. Add an empty group: right-click empty canvas -> "Add group". A tinted rectangle
   appears. Drag its title bar: every node whose center is inside the rectangle moves
   with it. Drag its bottom-right corner to resize.
2. Group a selection: rubber-band / Ctrl-click a few nodes, then right-click empty
   canvas -> "Group selected nodes". The new group wraps the selection.
3. Group context menu: right-click the group -> rename via the "Title" field, change
   its "Color" with the color widget, "Fit to nodes" (snap the rectangle back around
   its current members), "Delete group" (rectangle only, nodes survive) and
   "Delete group & contained nodes".
4. Del key: select a group and press Del -> only the rectangle is removed; the nodes
   inside stay.
5. Persistence: save the workspace (Ctrl+S), reopen; groups (title, color, position,
   size) should come back unchanged.
"""

import fiatlight as fl


@fl.with_fiat_attributes(fiat_tags=["math"])
def make_int() -> int:
    return 21


@fl.with_fiat_attributes(fiat_tags=["math"])
def double(x: int) -> int:
    return x * 2


@fl.with_fiat_attributes(fiat_tags=["math"])
def add_ten(x: int) -> int:
    return x + 10


@fl.with_fiat_attributes(fiat_tags=["text"])
def make_str() -> str:
    return "hello"


fl.run_graph_composer([make_int, double, add_ten, make_str], app_name="usability_node_groups")
