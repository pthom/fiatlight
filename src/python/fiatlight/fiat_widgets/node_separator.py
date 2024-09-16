from imgui_bundle import imgui
from imgui_bundle import imgui_node_editor as ed, ImVec2, hello_imgui
from typing import Callable
from fiatlight import fiat_utils

from dataclasses import dataclass


GuiFunction = Callable[[], None]


@dataclass
class NodeSeparatorParams:
    """Parameters for the node separator."""

    # The text to display
    text: str = ""
    # Whether to show the collapse button
    show_collapse_button: bool = False
    # Whether the separator is currently expanded
    # (if show_collapse_button is True)
    expanded: bool = True
    # Whether to show a button to toggle the collapse state of all inputs/outputs
    show_toggle_collapse_all_button: bool = False

    # The parent node
    parent_node: ed.NodeId | None = None


@dataclass
class NodeSeparatorOutput:
    """Output of the node separator."""

    was_expand_state_changed: bool = False
    expanded: bool = False
    was_toggle_collapse_all_clicked: bool = False


def node_separator_2(
    text: str = "",
    show_collapse_button: bool = False,
    expanded: bool = True,
    show_toggle_collapse_all_button: bool = False,
    parent_node: ed.NodeId | None = None,
) -> NodeSeparatorOutput:
    params = NodeSeparatorParams(
        text=text,
        show_collapse_button=show_collapse_button,
        expanded=expanded,
        show_toggle_collapse_all_button=show_toggle_collapse_all_button,
        parent_node=parent_node,
    )
    return node_separator(params)


def node_separator(params: NodeSeparatorParams) -> NodeSeparatorOutput:
    """Create a separator, possibly with a collapse button and a button to toggle the collapse state of all inputs/outputs.
    :return: tuple(was_expand_state_changed, is_expanded)
    """
    from fiatlight.fiat_widgets import icons_fontawesome_6, fontawesome_6_ctx
    from fiatlight.fiat_widgets import fiat_osd

    if params.parent_node is None:
        from fiatlight.fiat_nodes.function_node_gui import get_current_function_node_id

        params.parent_node = get_current_function_node_id()

    assert params.parent_node is not None

    result = NodeSeparatorOutput()
    result.expanded = params.expanded

    node_size = ed.get_node_size(params.parent_node)
    node_pos = ed.get_node_position(params.parent_node)

    spacing_y = imgui.get_style().item_spacing.y
    if len(params.text) > 0:
        spacing_y += imgui.get_font_size() + imgui.get_style().item_spacing.y

    spacing_x = imgui.get_style().item_spacing.x / 2.0

    cur_pos = imgui.get_cursor_screen_pos()
    if fiat_utils.is_rendering_in_node():
        p1 = ImVec2(node_pos.x + spacing_x, cur_pos.y + spacing_y / 2)
        p2 = ImVec2(p1.x + node_size.x - 1.0 - 2 * spacing_x, p1.y)
    else:
        p1 = ImVec2(cur_pos.x + spacing_x, cur_pos.y + spacing_y / 2)
        p2 = ImVec2(p1.x + imgui.get_content_region_avail().x - 1.0 - 2 * spacing_x, p1.y)

    # Collapse buttons placement
    btn_collapse_pos: ImVec2 | None = None
    btn_collapse_all_pos: ImVec2 | None = None
    y_collapse_buttons = p1.y - hello_imgui.em_size(0.6)
    x_collapse_buttons = p1.x + hello_imgui.em_size(0.1)
    if params.show_collapse_button:
        btn_collapse_pos = ImVec2(x_collapse_buttons, y_collapse_buttons)
        x_collapse_buttons += hello_imgui.em_size(2)
    if params.show_toggle_collapse_all_button:
        btn_collapse_all_pos = ImVec2(x_collapse_buttons, y_collapse_buttons)
        x_collapse_buttons += hello_imgui.em_size(2)

    p1.x = x_collapse_buttons

    thickness = hello_imgui.em_size(0.2)

    def get_color32(col: imgui.Col_) -> int:
        color = imgui.get_style().color_(col.value)
        return imgui.color_convert_float4_to_u32(color)

    def draw_line(a: ImVec2, b: ImVec2) -> None:
        color32 = get_color32(imgui.Col_.separator)
        imgui.get_window_draw_list().add_line(a, b, color32, thickness)

    def draw_separator_text() -> None:
        if len(params.text) == 0:
            draw_line(p1, p2)
        else:
            text = " " + params.text + " "
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

    draw_separator_text()

    if not params.show_collapse_button:
        result.expanded = True
    else:
        with fontawesome_6_ctx():
            assert btn_collapse_pos is not None
            imgui.set_cursor_screen_pos(btn_collapse_pos)
            if params.expanded:
                visible = not imgui.button(icons_fontawesome_6.ICON_FA_EYE + "##" + params.text)
                fiat_osd.set_widget_tooltip("Hide " + params.text)
                changed = visible != params.expanded
                result.was_expand_state_changed = changed
                result.expanded = visible
            else:
                visible = imgui.button(icons_fontawesome_6.ICON_FA_EYE_SLASH + "##" + params.text)
                fiat_osd.set_widget_tooltip("Show " + params.text)
                result.was_expand_state_changed = visible != params.expanded
                result.expanded = visible

    if params.show_toggle_collapse_all_button:
        with fontawesome_6_ctx():
            assert btn_collapse_all_pos is not None
            imgui.set_cursor_screen_pos(btn_collapse_all_pos)
            if imgui.button(icons_fontawesome_6.ICON_FA_COMPRESS + "##" + params.text):
                result.was_toggle_collapse_all_clicked = True
            fiat_osd.set_widget_tooltip("Toggle collapse state")

    imgui.set_cursor_screen_pos(ImVec2(cur_pos.x, cur_pos.y + spacing_y))

    return result
