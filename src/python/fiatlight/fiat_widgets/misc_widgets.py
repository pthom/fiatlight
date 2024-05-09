from imgui_bundle import imgui, ImVec4, hello_imgui, imgui_ctx
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
    info_tooltip: str | None = None,
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

    # Tooltip
    tooltip_str = None
    if info_tooltip is not None:
        tooltip_str = info_tooltip
    if is_truncated:
        if tooltip_str is not None:
            tooltip_str += "\n\n" + msg
    if tooltip_str is not None:
        fiat_osd.set_widget_tooltip(tooltip_str[:1000])


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


def button_with_disable_flag(label: str, is_disabled: bool) -> bool:
    if is_disabled:
        imgui.begin_disabled()
    clicked = imgui.button(label)
    if is_disabled:
        imgui.end_disabled()
    return clicked


def on_off_button_with_icons(is_on: bool, on_icon: str, off_icon: str) -> bool:
    icon = on_icon if is_on else off_icon
    # color: dark red if on, else dark gray
    color = ImVec4(1.0, 0.3, 0.3, 1.0) if is_on else ImVec4(0.7, 0.7, 0.7, 1.0)
    with imgui_ctx.push_style_color(imgui.Col_.text.value, color):
        with imgui_ctx.begin_horizontal("OnOffButton"):
            imgui.spring()
            button_size = hello_imgui.em_to_vec2(3, 3)
            clicked = imgui.button(icon, button_size)
            imgui.spring()
    return clicked
