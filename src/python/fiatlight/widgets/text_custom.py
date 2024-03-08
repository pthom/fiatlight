from imgui_bundle import imgui, ImVec4
from fiatlight.widgets import osd_widgets
from fiatlight.utils.registry import AutoRegistry
from typing import Callable


GuiFunction = Callable[[], None]


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


_EXPANDED_REGISTRY: AutoRegistry[bool] = AutoRegistry(bool)


def present_expandable_str(value_extract: str, value_full: str) -> None:
    from fiatlight.widgets import IconsFontAwesome6

    id = imgui.get_id("expand")  # it will be unique, since a lot of calls of imgui.push_id are made before
    is_expanded = _EXPANDED_REGISTRY.get(id)

    _, is_expanded = imgui.checkbox("Expand", is_expanded)
    _EXPANDED_REGISTRY[id] = is_expanded
    imgui.same_line()

    def detail_gui() -> None:
        imgui.input_text_multiline("##value_text", value_full)

    if imgui.button(IconsFontAwesome6.ICON_BOOK):
        osd_widgets.set_detail_gui(detail_gui)

    # if imgui.button(IconsFontAwesome6.ICON_BOOK):
    #     imgui.open_popup("expandable_str_popup")
    # imgui.set_next_window_pos(ed.canvas_to_screen(imgui.get_cursor_pos()), imgui.Cond_.appearing.value)
    # if imgui.begin_popup("expandable_str_popup"):
    #     imgui.input_text_multiline("##value_text", value_full, ImVec2(0, hello_imgui.em_size(15)))
    #     imgui.end_popup()

    if imgui.is_item_hovered():
        osd_widgets.set_tooltip("Click to show details, then open the Info tab at the bottom to see the full string")
    imgui.same_line()
    if imgui.button(IconsFontAwesome6.ICON_COPY):
        imgui.set_clipboard_text(value_full)
    if imgui.is_item_hovered():
        osd_widgets.set_tooltip("Copy to clipboard")

    if not is_expanded:
        imgui.text(value_extract + "\n[...]")
    else:
        imgui.text(value_full)
