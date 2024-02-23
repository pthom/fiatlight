from imgui_bundle import imgui, ImVec4
from fiatlight.internal import osd_widgets
from fiatlight.fiatlight_types import VoidFunction
from imgui_bundle import imgui_node_editor as ed, ImVec2, hello_imgui
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


def node_separator(parent_node: ed.NodeId, text: str = "") -> None:
    node_size = ed.get_node_size(parent_node)
    node_pos = ed.get_node_position(parent_node)

    spacing_y = imgui.get_style().item_spacing.y
    if len(text) > 0:
        spacing_y += imgui.get_font_size() + imgui.get_style().item_spacing.y

    spacing_x = imgui.get_style().item_spacing.x / 2.0

    cur_pos = imgui.get_cursor_screen_pos()
    p1 = ImVec2(node_pos.x + spacing_x, cur_pos.y + spacing_y / 2)
    p2 = ImVec2(p1.x + node_size.x - 1.0 - 2 * spacing_x, p1.y)

    thickness = hello_imgui.em_size(0.2)

    def get_color32(col: imgui.Col_) -> int:
        color = imgui.get_style().color_(col.value)
        return imgui.color_convert_float4_to_u32(color)

    def draw_line(p1: ImVec2, p2: ImVec2) -> None:
        color32 = get_color32(imgui.Col_.separator)
        imgui.get_foreground_draw_list().add_line(ed.canvas_to_screen(p1), ed.canvas_to_screen(p2), color32, thickness)

    if len(text) == 0:
        draw_line(p1, p2)
    else:
        text = " " + text + " "
        text_size = imgui.calc_text_size(text)
        p11 = p1
        p12 = ImVec2(p1.x + (p2.x - p1.x - text_size.x) / 4, p1.y)
        p21 = ImVec2(p12.x + text_size.x, p12.y)
        p22 = p2
        draw_line(p11, p12)
        draw_line(p21, p22)
        p_text = ImVec2(p12.x, p12.y - imgui.get_font_size() / 2)
        orig_cursor_pos = imgui.get_cursor_screen_pos()
        imgui.set_cursor_screen_pos(p_text)
        text_custom(text)
        imgui.set_cursor_screen_pos(orig_cursor_pos)
    imgui.dummy(ImVec2(0, spacing_y))
