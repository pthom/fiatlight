from imgui_bundle import imgui, ImVec4, imgui_ctx, hello_imgui
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
    additional_tooltip: str | None = None,
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


_ON_OFF_BUTTON_HOVER_REGISTRY: AutoRegistry[bool] = AutoRegistry(bool)


def on_off_button(
    label_id: str, is_on: bool, icon_off: str = "", icon_on: str = "", tooltip_off: str = "", tooltip_on: str = ""
) -> bool:
    id_ = imgui.get_id(label_id)
    is_mouse_hovered = _ON_OFF_BUTTON_HOVER_REGISTRY.get(id_)  # from last frame

    button_size = hello_imgui.em_to_vec2(3, 3)

    icon = icon_on if is_on else icon_off
    if is_mouse_hovered:
        icon = icon_off if is_on else icon_on

    tooltip = tooltip_on if is_on else tooltip_off

    # text_color: dark red if on, else dark gray
    orange = ImVec4(1.0, 0.5, 0.0, 1.0)
    gray = ImVec4(0.7, 0.7, 0.7, 1.0)
    orange_gray = ImVec4(0.9, 0.6, 0.2, 1.0)
    text_color = orange if is_on else gray
    if is_mouse_hovered:
        text_color = orange_gray

    with imgui_ctx.push_style_color(imgui.Col_.text.value, text_color):
        clicked = imgui.button(icon, button_size)
    fiat_osd.set_widget_tooltip(tooltip)
    _ON_OFF_BUTTON_HOVER_REGISTRY[id_] = imgui.is_item_hovered()
    return clicked
