"""Classic group: a tinted, titled, resizable rectangle drawn behind nodes.

Pure organization, ComfyUI-style: a group has **no pins, no type, no execution**, and
never enters the headless `fiat_core` graph. It is GUI-only state owned by
`FunctionsGraphGui` and persisted in the workspace JSON (alongside node positions).

Dragging the rectangle drags every node whose center falls inside it, handled
*internally* by `imgui_node_editor` (its DragAction). Membership is therefore geometric,
not a maintained set; bulk operations (fit-to-nodes, delete-with-nodes) recompute it from
node centers on demand.

The data/view split mirrors the reroute node: `NodeGroup` is the plain serializable shape
(it *is* the JSON object), `NodeGroupGui` is the view that owns the editor `NodeId` and
renders it.
"""

from __future__ import annotations

from dataclasses import dataclass

from fiatlight.fiat_types import JsonDict
from imgui_bundle import imgui, imgui_node_editor as ed, ImVec2, ImVec4

# Preset tints (RGB), used to seed a new group's color. The user can then freely change it
# with the color widget in the group's context menu. The background fill is drawn
# translucent and the border nearly opaque, both derived from the group's RGB color.
GROUP_COLOR_PRESETS: list[tuple[float, float, float]] = [
    (0.26, 0.59, 0.98),  # blue
    (0.40, 0.80, 0.45),  # green
    (0.95, 0.62, 0.25),  # orange
    (0.80, 0.45, 0.85),  # magenta
    (0.55, 0.56, 0.62),  # gray
]


@dataclass
class NodeGroup:
    """Plain serializable state of a classic group. This is exactly the JSON object
    written under the workspace's ``"groups"`` array.

    `position` is the top-left of the node (its title strip); `size` is the colored
    rectangle below the title (what we hand to `ed.group`), *not* the full node height.
    `color` is the group's base RGB tint (alpha for fill/border is derived at draw time).
    """

    title: str
    color: tuple[float, float, float]
    position: tuple[float, float]
    size: tuple[float, float]

    def to_json(self) -> JsonDict:
        return {
            "title": self.title,
            "color": [self.color[0], self.color[1], self.color[2]],
            "position": [self.position[0], self.position[1]],
            "size": [self.size[0], self.size[1]],
        }

    @staticmethod
    def from_json(data: JsonDict) -> "NodeGroup":
        color = data.get("color", list(GROUP_COLOR_PRESETS[0]))
        pos = data.get("position", [0.0, 0.0])
        size = data.get("size", [260.0, 180.0])
        return NodeGroup(
            title=str(data.get("title", "Group")),
            color=(float(color[0]), float(color[1]), float(color[2])),
            position=(float(pos[0]), float(pos[1])),
            size=(float(size[0]), float(size[1])),
        )


class NodeGroupGui:
    """View for a `NodeGroup`: owns the editor node id and renders the group rectangle."""

    def __init__(self, group: NodeGroup) -> None:
        self.group = group
        self._ed_node_id = ed.NodeId.create()
        # Height the title strip consumed at the last draw, measured live (one text line).
        # Used when saving to convert the editor's full node size back into the rect size.
        self._header_height: float = imgui.get_text_line_height_with_spacing()

    def node_id(self) -> ed.NodeId:
        return self._ed_node_id

    def draw(self) -> None:
        r, g, b = self.group.color
        ed.push_style_color(ed.StyleColor.group_bg, ImVec4(r, g, b, 0.18))
        ed.push_style_color(ed.StyleColor.group_border, ImVec4(r, g, b, 0.85))
        ed.begin_node(self._ed_node_id)
        y0 = imgui.get_cursor_pos_y()
        imgui.text_unformatted(self.group.title)
        # Header = everything between begin_node and group(); here just the one title line.
        self._header_height = imgui.get_cursor_pos_y() - y0
        ed.group(ImVec2(self.group.size[0], self.group.size[1]))
        ed.end_node()
        ed.pop_style_color(2)
