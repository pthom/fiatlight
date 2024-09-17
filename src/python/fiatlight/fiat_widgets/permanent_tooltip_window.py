from imgui_bundle import imgui, ImVec2, imgui_ctx, hello_imgui
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class CornerPosition(Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3


def compute_corner_position_from_window(
    gui_size: ImVec2, padding_em: ImVec2, position: CornerPosition, parent_window: imgui.internal.Window | None = None
) -> ImVec2:
    if parent_window is None:
        parent_window = imgui.internal.get_current_window()
    parent_window_pos = parent_window.pos
    parent_window_size = parent_window.size

    padding_pixels = hello_imgui.em_to_vec2(padding_em.x, padding_em.y)
    child_window_pos = ImVec2()
    if position == CornerPosition.TOP_LEFT:
        child_window_pos = ImVec2(parent_window_pos.x + padding_pixels.x, parent_window_pos.y + padding_pixels.y)
    elif position == CornerPosition.TOP_RIGHT:
        child_window_pos = ImVec2(
            parent_window_pos.x + parent_window_size.x - gui_size.x - padding_pixels.x,
            parent_window_pos.y + padding_pixels.y,
        )
    elif position == CornerPosition.BOTTOM_LEFT:
        child_window_pos = ImVec2(
            parent_window_pos.x + padding_pixels.x,
            parent_window_pos.y + parent_window_size.y - gui_size.y - padding_pixels.y,
        )
    elif position == CornerPosition.BOTTOM_RIGHT:
        child_window_pos = ImVec2(
            parent_window_pos.x + parent_window_size.x - gui_size.x - padding_pixels.x,
            parent_window_pos.y + parent_window_size.y - gui_size.y - padding_pixels.y,
        )
    return child_window_pos


@dataclass
class PermanentTooltipOptions:
    no_border: bool = False
    no_background: bool = False
    padding_em: tuple[float, float] = (0.5, 0.5)
    position: CornerPosition = CornerPosition.TOP_LEFT


def show_permanent_tooltip_window(
    gui_func: Callable[[], None], options: PermanentTooltipOptions = PermanentTooltipOptions()
) -> None:
    parent_window = imgui.internal.get_current_window()

    flags = (
        0
        | imgui.WindowFlags_.no_decoration.value
        | imgui.WindowFlags_.no_move.value
        | imgui.WindowFlags_.always_auto_resize.value
        | imgui.WindowFlags_.no_saved_settings.value
        | imgui.WindowFlags_.no_focus_on_appearing.value
        | imgui.WindowFlags_.no_bring_to_front_on_focus.value
        | imgui.WindowFlags_.no_nav.value
        # | imgui.WindowFlags_.tooltip.value  # marked as "Don't use" in the imgui source code
    )
    if options.no_background:
        flags |= imgui.WindowFlags_.no_background.value
    if options.no_border:
        imgui.push_style_var(imgui.StyleVar_.window_border_size.value, 0.0)
    with imgui_ctx.begin("##TopRightTooltip", None, flags):
        gui_func()
        child_window_size = imgui.get_window_size()
        padding_em_vec = ImVec2(options.padding_em[0], options.padding_em[1])
        child_window_pos = compute_corner_position_from_window(
            gui_size=child_window_size,
            padding_em=padding_em_vec,
            position=options.position,
            parent_window=parent_window,
        )

        imgui.set_window_pos(child_window_pos)

    if options.no_border:
        imgui.pop_style_var()
