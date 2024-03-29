from imgui_bundle import imgui, ImVec4
from fiatlight.fiat_widgets import fiat_osd
from fiatlight.fiat_utils.registry import AutoRegistry
from typing import Callable, Tuple


GuiFunction = Callable[[], None]


_EXPANDED_REGISTRY: AutoRegistry[bool] = AutoRegistry(bool)


def _truncate_text(
    msg: str,
    *,
    max_width_pixels: float | None = None,
    max_width_chars: int | None = None,
    max_lines: int | None = None,
) -> Tuple[bool, str]:
    assert max_width_pixels is None or max_width_chars is None

    if max_width_pixels is not None:
        font_approx_width = imgui.get_font_size() * 0.8
        max_width_chars = int(max_width_pixels / font_approx_width)

    if len(msg) == 0:
        return False, msg

    is_truncated = False

    def truncate_line(line: str) -> str:
        nonlocal is_truncated
        if max_width_chars is None:
            return line
        if len(line) > max_width_chars:
            is_truncated = True
            return line[:max_width_chars] + "..."
        return line

    def truncate_lines() -> list[str]:
        nonlocal is_truncated
        lines = msg.split("\n")
        if max_lines is not None and len(lines) > max_lines:
            is_truncated = True
            lines = lines[:max_lines]
            lines[-1] += " (...)"
        return lines

    truncated_y = truncate_lines()
    truncated_x = [truncate_line(line) for line in truncated_y]
    new_msg = "\n".join(truncated_x)
    return is_truncated, new_msg


def text_maybe_truncated(
    msg: str,
    *,
    color: ImVec4 | None = None,
    max_width_pixels: float | None = None,
    max_width_chars: int | None = None,
    max_lines: int | None = None,
    show_full_as_tooltip: bool = True,
) -> None:
    def output_text(s: str) -> None:
        if color is not None:
            imgui.text_colored(color, s)
        else:
            imgui.text(s)

    is_truncated, msg_truncated = _truncate_text(
        msg,
        max_width_pixels=max_width_pixels,
        max_width_chars=max_width_chars,
        max_lines=max_lines,
    )

    output_text(msg_truncated)
    if is_truncated and show_full_as_tooltip:
        fiat_osd.set_widget_tooltip(msg[:1000])


def collapsible_button(expanded: bool, tooltip_part: str) -> bool:
    """A button that toggles between expanded and collapsed states.
    Returns true if expanded, false if collapsed.
    Displays as a caret pointing down if expanded, and right if collapsed, as imgui.collapsing_header() does.
    """
    from fiatlight.fiat_widgets.fontawesome6_ctx_utils import fontawesome_6_ctx, icons_fontawesome_6

    icon = icons_fontawesome_6.ICON_FA_CARET_DOWN if expanded else icons_fontawesome_6.ICON_FA_CARET_RIGHT
    tooltip = "Hide " + tooltip_part if expanded else "Show " + tooltip_part
    with fontawesome_6_ctx():
        clicked = imgui.button(icon)
        fiat_osd.set_widget_tooltip(tooltip)
        if not clicked:
            return expanded
        else:
            return not expanded
