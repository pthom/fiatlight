from imgui_bundle import imgui, ImVec4
from fiatlight.internal import osd_widgets


def text(msg: str, max_line_width: int | None = None, color: ImVec4 | None = None) -> None:
    msg_orig = msg
    is_truncated = False

    if max_line_width is not None:

        def truncate_line(line: str) -> str:
            if len(line) > max_line_width:
                nonlocal is_truncated
                is_truncated = True
                return line[:max_line_width] + "..."
            return line

        lines = msg.split("\n")
        msg = "\n".join(truncate_line(line) for line in lines)

    if color is not None:
        imgui.text_colored(color, msg)
    else:
        imgui.text(msg)

    if is_truncated and imgui.is_item_hovered():
        osd_widgets.set_tooltip(msg_orig)
