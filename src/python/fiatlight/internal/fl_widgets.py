from imgui_bundle import imgui, ImVec4
from fiatlight.internal import osd_widgets


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
