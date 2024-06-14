from imgui_bundle import ImVec4, imgui
from fiatlight.fiat_widgets import fiat_osd
from pydantic import BaseModel
from typing import Tuple


class TruncationParams(BaseModel):
    # Maximum number of characters to display in a string before truncation
    max_characters: int | None = None
    # Maximum number of lines to display in a string before truncation
    max_lines: int | None = None


def _truncate_text(msg: str, params: TruncationParams) -> Tuple[bool, str]:
    if len(msg) == 0:
        return False, msg

    is_truncated = False

    def truncate_line(line: str) -> str:
        nonlocal is_truncated
        if params.max_characters is None:
            return line
        if len(line) > params.max_characters:
            is_truncated = True
            return line[: params.max_characters] + "..."
        return line

    def truncate_lines() -> list[str]:
        nonlocal is_truncated
        lines = msg.split("\n")
        if params.max_lines is not None and len(lines) > params.max_lines:
            is_truncated = True
            lines = lines[: params.max_lines]
            lines[-1] += " (...)"
        return lines

    truncated_y = truncate_lines()
    truncated_x = [truncate_line(line) for line in truncated_y]
    new_msg = "\n".join(truncated_x)
    return is_truncated, new_msg


def text_maybe_truncated(
    msg: str,
    params: TruncationParams,
    *,
    color: ImVec4 | None = None,
    additional_tooltip: str | None = None,
) -> None:
    def output_text(s: str) -> None:
        if color is not None:
            imgui.text_colored(color, s)
        else:
            imgui.text(s)

    is_truncated, msg_truncated = _truncate_text(msg, params)

    output_text(msg_truncated)

    # Tooltip
    tooltip_str = ""
    if additional_tooltip is not None:
        tooltip_str = additional_tooltip
    if is_truncated:
        if len(tooltip_str) > 0:
            tooltip_str += "\n\n" + msg
        else:
            tooltip_str = msg
    if len(tooltip_str) > 0:
        fiat_osd.set_widget_tooltip(tooltip_str[:1000])
