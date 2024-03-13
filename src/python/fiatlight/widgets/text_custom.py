from imgui_bundle import imgui, ImVec4
from fiatlight.widgets import osd_widgets
from fiatlight.utils.registry import AutoRegistry
from typing import Callable, Tuple


GuiFunction = Callable[[], None]


_EXPANDED_REGISTRY: AutoRegistry[bool] = AutoRegistry(bool)


def _truncate_text(
    msg: str,
    *,
    max_width_pixels: float | None = None,
    max_width_chars: int | None = None,
    max_lines: int | None = None,
    remove_after_double_hash: bool = True,
) -> Tuple[bool, str]:
    assert max_width_pixels is None or max_width_chars is None

    if max_width_pixels is not None:
        font_approx_width = imgui.get_font_size() * 0.8
        max_width_chars = int(max_width_pixels / font_approx_width)

    if remove_after_double_hash:
        msg = msg.split("##", 1)[0]

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
            lines.append("...")
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
    remove_after_double_hash: bool = True,
    show_expand_checkbox: bool = False,
    show_full_as_tooltip: bool = True,
    show_copy_button: bool = False,
    show_details_button: bool = False,
) -> None:
    from imgui_bundle import icons_fontawesome_4

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
        remove_after_double_hash=remove_after_double_hash,
    )

    flag_shown_button = False

    if show_expand_checkbox and is_truncated:
        expand_id = imgui.get_id("expand")  # it will be unique, since a lot of calls of imgui.push_id are made before
        is_expanded = _EXPANDED_REGISTRY.get(expand_id)
        _, is_expanded = imgui.checkbox("Expand", is_expanded)
        _EXPANDED_REGISTRY[expand_id] = is_expanded
        if is_expanded:
            msg_truncated = msg
        imgui.same_line()
        flag_shown_button = True

    if show_copy_button:
        if imgui.button(icons_fontawesome_4.ICON_FA_COPY):
            imgui.set_clipboard_text(msg)
        if imgui.is_item_hovered():
            osd_widgets.set_tooltip("Copy to clipboard")
        imgui.same_line()
        flag_shown_button = True

    if is_truncated and show_details_button:
        if imgui.button(icons_fontawesome_4.ICON_FA_BOOK):

            def detail_gui() -> None:
                imgui.input_text_multiline("##value_text", msg)

            osd_widgets.set_detail_gui(detail_gui)
        if imgui.is_item_hovered():
            osd_widgets.set_tooltip(
                "Click to show details, then open the Info tab at the bottom to see the full string"
            )
        imgui.same_line()
        flag_shown_button = True

    if flag_shown_button:
        imgui.new_line()

    output_text(msg_truncated)
    if is_truncated and show_full_as_tooltip and imgui.is_item_hovered():
        osd_widgets.set_tooltip(msg[:3000])
