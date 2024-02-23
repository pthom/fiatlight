from imgui_bundle import imgui, ImVec4
from fiatlight.internal import osd_widgets
from fiatlight.fiatlight_types import VoidFunction
from imgui_bundle import imgui_node_editor as ed
from typing import Dict


def text_custom(
    msg: str, max_width_pixels: float | None = None, color: ImVec4 | None = None, remove_after_double_hash: bool = True
) -> None:
    if remove_after_double_hash:
        msg = msg.split("##", 1)[0]
    if len(msg) == 0:
        return

    msg_orig = msg
    is_truncated = False

    def truncate_line(line: str, max_chars: int) -> str:
        if len(line) > max_chars:
            nonlocal is_truncated
            is_truncated = True
            return line[:max_chars] + "..."
        return line

    def truncate_lines(max_chars: int) -> str:
        lines = msg.split("\n")
        return "\n".join(truncate_line(line, max_chars) for line in lines)

    if max_width_pixels is not None:
        font_approx_width = imgui.get_font_size() * 0.8
        max_chars = int(max_width_pixels / font_approx_width)
        msg = truncate_lines(max_chars)

    if color is not None:
        imgui.text_colored(color, msg)
    else:
        imgui.text(msg)

    if is_truncated and imgui.is_item_hovered():
        osd_widgets.set_tooltip(msg_orig)


RIGHT_ALIGN_WIDTH: Dict[int, float] = {}


def draw_node_gui_right_align(parent_node: ed.NodeId, gui_function: VoidFunction) -> None:
    parent_size = ed.get_node_size(parent_node)
    item_id = imgui.get_id("align_right")
    imgui.push_id(str(item_id))

    if item_id not in RIGHT_ALIGN_WIDTH.keys():
        pos_x = 0.0
    else:
        pos_x = parent_size.x - RIGHT_ALIGN_WIDTH[item_id]

    imgui.same_line(pos_x)
    imgui.begin_group()
    gui_function()
    imgui.end_group()
    RIGHT_ALIGN_WIDTH[item_id] = imgui.get_item_rect_size().x + 20  # 20 ???

    # print(f"RIGHT_ALIGN_WIDTH: {RIGHT_ALIGN_WIDTH[item_id]} parent_size.x: {parent_size.x} pos_x: {pos_x}")

    imgui.pop_id()
