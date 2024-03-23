from imgui_bundle import imgui
from imgui_bundle import imgui_node_editor as ed, ImVec2, hello_imgui
from typing import Callable


GuiFunction = Callable[[], None]


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
        imgui.get_window_draw_list().add_line(p1, p2, color32, thickness)

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
        imgui.text(text)
        imgui.set_cursor_screen_pos(orig_cursor_pos)
    imgui.dummy(ImVec2(0, spacing_y))
