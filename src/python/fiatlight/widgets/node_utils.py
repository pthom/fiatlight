from imgui_bundle import imgui
from fiatlight.utils.registry import AutoRegistry
from imgui_bundle import imgui_node_editor as ed, ImVec2, hello_imgui
from typing import Callable
from dataclasses import dataclass


GuiFunction = Callable[[], None]


@dataclass
class _RightAlignData:
    parent_width: float = 0
    item_width: float = 0


class _RightAlign:
    align_datas: AutoRegistry[_RightAlignData]

    def __init__(self) -> None:
        self.align_datas = AutoRegistry(_RightAlignData)

    def right_align(self, item_id: int, parent_width: float, gui_function: GuiFunction) -> None:
        right_align_data = self.align_datas.get(item_id)
        pos_x = 1000.0
        right_margin = hello_imgui.em_size(0.8)
        if parent_width == right_align_data.parent_width and right_align_data.item_width > 0:
            pos_x = parent_width - right_align_data.item_width - right_margin

        dc = imgui.get_current_context().current_window.dc
        cursor_max_pos_x = dc.cursor_max_pos.x
        cursor_pos_prev_line_x = dc.cursor_pos_prev_line.x

        imgui.same_line(pos_x)
        imgui.begin_group()
        gui_function()
        imgui.end_group()
        dc.cursor_max_pos.x = cursor_max_pos_x
        dc.cursor_pos_prev_line.x = cursor_pos_prev_line_x

        right_align_data.item_width = imgui.get_item_rect_size().x
        right_align_data.parent_width = parent_width


_RIGHT_ALIGN = _RightAlign()


def draw_node_gui_right_align(parent_node: ed.NodeId, gui_function: GuiFunction) -> None:
    parent_size = ed.get_node_size(parent_node)
    item_id = imgui.get_id("align_right")  # will be unique for each item, since imgui.push_id is used before
    _RIGHT_ALIGN.right_align(item_id, parent_size.x, gui_function)


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
        imgui.text(text)
        imgui.set_cursor_screen_pos(orig_cursor_pos)
    imgui.dummy(ImVec2(0, spacing_y))


def sandbox():
    from imgui_bundle import immapp

    node_id = ed.NodeId(1)

    def gui():
        ed.begin("editor")
        ed.begin_node(node_id)

        imgui.dummy(ImVec2(100, 10))

        imgui.text("ABCDEFGHUDD")
        imgui.same_line()

        draw_node_gui_right_align(node_id, lambda: imgui.text("Right Align"))

        ed.end_node()
        ed.end()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
