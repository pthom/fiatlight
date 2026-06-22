import contextlib
from typing import Generator

from imgui_bundle import ImVec2, ImVec4, imgui, imgui_ctx, hello_imgui
from fiatlight.fiat_widgets import fiat_osd
from fiatlight.fiat_utils.fiat_node_semaphore import is_rendering_in_node
from pydantic import BaseModel
from typing import Tuple


# Width (px) kept free to the right of in-node truncated text, so a wide value truncates earlier
# instead of crowding the trailing header-line icons. Set via node_text_right_reserve().
_NODE_TEXT_RIGHT_RESERVE_PX: float = 0.0


@contextlib.contextmanager
def node_text_right_reserve(reserve_px: float) -> Generator[None, None, None]:
    """Within this context, in-node truncated text reserves `reserve_px` to its right (e.g. for
    the trailing detach / clipboard / output-pin icons), so a wide or multi-line value truncates
    before them instead of overlapping. Works through the present-callback boundary (str / list /
    image presenters all funnel into text_maybe_truncated)."""
    global _NODE_TEXT_RIGHT_RESERVE_PX
    previous = _NODE_TEXT_RIGHT_RESERVE_PX
    _NODE_TEXT_RIGHT_RESERVE_PX = reserve_px
    try:
        yield
    finally:
        _NODE_TEXT_RIGHT_RESERVE_PX = previous


class TruncationParams(BaseModel):
    # Maximum width (in em) of a line before it is truncated with a trailing ellipsis.
    # Width-based (not a character count) so it matches the pixel space available in a node
    # and so that all truncated lines end at the same width. Only applied inside a node.
    max_width_em: float | None = None
    # Maximum number of (logical, newline-separated) lines to display before truncation
    max_lines: int | None = None


def _truncate_lines(msg: str, max_lines: int | None) -> Tuple[bool, list[str]]:
    lines = msg.split("\n")
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] += " (...)"
        return True, lines
    return False, lines


def _ellipsis_to_width(line: str, max_width_pixels: float) -> Tuple[bool, str]:
    """Longest prefix of `line` that fits in max_width_pixels, with a trailing ellipsis if it
    was truncated.

    Binary search (O(log n) measurements), with a cheap character pre-cap so a very long line is
    never measured character by character: that linear scan ran every frame and froze the app on
    large in-node text.
    """
    if max_width_pixels <= 0:
        return len(line) > 0, "..."
    # No glyph is narrower than ~2px, so at most max_width_pixels/2 characters can possibly fit.
    # Slice to that (plus slack) before any measurement, to bound the work on huge lines.
    char_cap = int(max_width_pixels / 2) + 4
    if len(line) <= char_cap and imgui.calc_text_size(line).x <= max_width_pixels:
        return False, line
    capped = line[:char_cap]
    lo, hi = 0, len(capped)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if imgui.calc_text_size(capped[:mid] + "...").x <= max_width_pixels:
            lo = mid
        else:
            hi = mid - 1
    return True, capped[:lo] + "..."


def text_colored_no_wrap(color: ImVec4, text: str) -> None:
    """Colored text with wrapping disabled. A short status literal ("Unspecified", "Error",
    "Default value:") shown in a node would otherwise collapse into a one-character column on a
    narrow node, because imgui-node-editor pushes a text wrap pos at the node's right edge."""
    with imgui_ctx.push_text_wrap_pos(-1.0):
        imgui.text_colored(color, text)


def draw_label_with_max_width(
    label: str,
    color: ImVec4,
    max_width_em: float,
    label_tooltip: str | None,
    status_tooltip: str | None = None,
    id_tooltip: str | None = None,
) -> None:
    """Draw a label truncated (with an ellipsis) to `max_width_em`, reserving exactly that width
    so following content lines up across rows. Full text + the given tooltips go to a tooltip."""
    segments = [s for s in (label_tooltip, id_tooltip, status_tooltip) if s]
    tooltip = "\n----------------------------------\n".join(segments)

    cur_pos = imgui.get_cursor_screen_pos()
    if "##" in label:
        label = label.split("##")[0]
    max_width_pixels = hello_imgui.em_size(max_width_em)
    truncated, shown_label = _ellipsis_to_width(label, max_width_pixels)
    imgui.text_colored(color, shown_label)
    if truncated:
        tooltip = label + "\n" + tooltip

    if len(tooltip) > 0:
        fiat_osd.set_widget_tooltip(tooltip)

    new_cursor_pos = ImVec2(cur_pos.x + max_width_pixels, cur_pos.y)
    imgui.set_cursor_screen_pos(new_cursor_pos)


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

    is_truncated, lines = _truncate_lines(msg, params.max_lines)

    if is_rendering_in_node() and params.max_width_em is not None:
        # In a node: clamp each line to the em budget AND to the room actually left in the
        # node (so the text never overflows / clips at the node border on a narrow node), then
        # disable imgui-node-editor's wrap-at-node-edge so the ellipsized lines stay on one
        # visual line each (no per-character column).
        max_width_pixels = hello_imgui.em_size(params.max_width_em)
        # Room left to the right of the cursor, minus the reserve kept for trailing icons.
        # Clamp to >= 0: when the reserve exceeds the room (a narrow node where the value
        # starts within the icon block), the value must collapse to an ellipsis rather than
        # fall back to the full em budget, which would render at full width and overflow the
        # node border.
        available = max(imgui.get_content_region_avail().x - _NODE_TEXT_RIGHT_RESERVE_PX, 0.0)
        max_width_pixels = min(max_width_pixels, available)
        clamped_lines = []
        for line in lines:
            line_truncated, clamped = _ellipsis_to_width(line, max_width_pixels)
            is_truncated = is_truncated or line_truncated
            clamped_lines.append(clamped)
        with imgui_ctx.push_text_wrap_pos(-1.0):
            output_text("\n".join(clamped_lines))
    else:
        # Outside a node (detached popup / focused window): render as-is, wrapping to the window.
        output_text("\n".join(lines))

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
