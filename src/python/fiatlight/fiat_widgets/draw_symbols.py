from imgui_bundle import ImVec2, imgui
from enum import Enum

ImU32 = int


class SymbolDrawing(Enum):
    ArrowUp = 0
    ArrowDown = 1
    Zero = 2


def _draw_zero(x0: float, y0: float, x1: float, y1: float, color: ImU32) -> None:
    c = ImVec2((x0 + x1) / 2, (y0 + y1) / 2)
    r = (x1 - x0) / 2
    imgui.get_window_draw_list().add_circle(c, r, color, thickness=1.5)


def _draw_arrow_up(x0: float, y0: float, x1: float, y1: float, color: ImU32) -> None:
    a = ImVec2(x0, y1)
    b = ImVec2(x1, y1)
    c = ImVec2((x0 + x1) / 2, y0)
    # The rendering differs if clockwise or counter-clockwise, thus we need to be careful with the order of the points.
    imgui.get_window_draw_list().add_triangle_filled(a, c, b, color)


def _draw_arrow_down(x0: float, y0: float, x1: float, y1: float, color: ImU32) -> None:
    a = ImVec2(x0, y0)
    b = ImVec2(x1, y0)
    c = ImVec2((x0 + x1) / 2, y1)
    imgui.get_window_draw_list().add_triangle_filled(a, b, c, color)


def _draw_symbol(x0: float, y0: float, x1: float, y1: float, symbol: SymbolDrawing) -> None:
    color = imgui.get_color_u32(imgui.Col_.text.value)
    if symbol == SymbolDrawing.ArrowUp:
        _draw_arrow_up(x0, y0, x1, y1, color)
    elif symbol == SymbolDrawing.ArrowDown:
        _draw_arrow_down(x0, y0, x1, y1, color)
    elif symbol == SymbolDrawing.Zero:
        _draw_zero(x0, y0, x1, y1, color)


def draw_symbol(pos: ImVec2, size: ImVec2, symbol: SymbolDrawing, reduce_size_factor: float = 0.6) -> None:
    xc = pos.x + size.x / 2
    yc = pos.y + size.y / 2
    w = size.x / 2 * reduce_size_factor
    h = size.y / 2 * reduce_size_factor

    _draw_symbol(xc - w, yc - h, xc + w, yc + h, symbol)
