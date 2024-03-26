from imgui_bundle import imgui
from imgui_bundle import imgui_node_editor as ed, ImVec2, hello_imgui
from typing import Callable, Tuple


GuiFunction = Callable[[], None]


def _node_separator(parent_node: ed.NodeId, text: str, show_collapse_button: bool, expanded: bool) -> Tuple[bool, bool]:
    """Create a separator, possibly with a collapse button.
    :return: tuple(was_expand_state_changed, is_expanded)
    """
    node_size = ed.get_node_size(parent_node)
    node_pos = ed.get_node_position(parent_node)

    spacing_y = imgui.get_style().item_spacing.y
    if len(text) > 0:
        spacing_y += imgui.get_font_size() + imgui.get_style().item_spacing.y

    spacing_x = imgui.get_style().item_spacing.x / 2.0

    cur_pos = imgui.get_cursor_screen_pos()
    p1 = ImVec2(node_pos.x + spacing_x, cur_pos.y + spacing_y / 2)
    p2 = ImVec2(p1.x + node_size.x - 1.0 - 2 * spacing_x, p1.y)

    btn_pos = ImVec2(p1.x + hello_imgui.em_size(0.1), p1.y - hello_imgui.em_size(0.6))

    if show_collapse_button:
        p1.x = btn_pos.x + hello_imgui.em_size(2)

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

    if show_collapse_button:
        from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx
        from fiatlight.fiat_widgets import fiat_osd

        with fontawesome_6_ctx():
            imgui.set_cursor_pos(btn_pos)

            if expanded:
                visible = not imgui.button(icons_fontawesome_6.ICON_FA_EYE + "##" + text)
                if imgui.is_item_hovered():
                    fiat_osd.set_tooltip("Collapse all")
                changed = visible != expanded
                return changed, visible
            else:
                visible = imgui.button(icons_fontawesome_6.ICON_FA_EYE_SLASH + "##" + text)
                if imgui.is_item_hovered():
                    fiat_osd.set_tooltip("Expand all")
                changed = visible != expanded
                return changed, visible

    else:
        imgui.set_cursor_pos(ImVec2(cur_pos.x, cur_pos.y + spacing_y))
        return False, True


def node_separator(parent_node: ed.NodeId, text: str) -> None:
    """Create a separator.
    parent_node: The node that contains the separator.
    text: The text to display in the separator.
    """
    _node_separator(parent_node, text, False, False)


def node_collapsing_separator(parent_node: ed.NodeId, text: str, expanded: bool) -> Tuple[bool, bool]:
    """Create a separator with a collapse button.
    parent_node: The node that contains the separator.
    text: The text to display in the separator.
    collapsed: Whether the separator is collapsed.
    return: tuple(was_expand_state_changed, is_expanded)
    """
    r = _node_separator(parent_node, text, True, expanded)
    return r
