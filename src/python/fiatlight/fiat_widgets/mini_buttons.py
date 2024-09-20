from imgui_bundle import ImVec2, imgui, hello_imgui
from enum import Enum
import copy

ImU32 = int


class _SymbolDrawing(Enum):
    ArrowUp = 0
    ArrowDown = 1
    Zero = 2
    Minus = 3


def _draw_minus(x0: float, y0: float, x1: float, y1: float, color: ImU32) -> None:
    yc = (y0 + y1) / 2
    imgui.get_window_draw_list().add_line(ImVec2(x0, yc), ImVec2(x1, yc), color, 1.5)


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


def _draw_symbol_impl(x0: float, y0: float, x1: float, y1: float, symbol: _SymbolDrawing) -> None:
    color = imgui.get_color_u32(imgui.Col_.text.value)
    if symbol == _SymbolDrawing.ArrowUp:
        _draw_arrow_up(x0, y0, x1, y1, color)
    elif symbol == _SymbolDrawing.ArrowDown:
        _draw_arrow_down(x0, y0, x1, y1, color)
    elif symbol == _SymbolDrawing.Zero:
        _draw_zero(x0, y0, x1, y1, color)
    elif symbol == _SymbolDrawing.Minus:
        _draw_minus(x0, y0, x1, y1, color)


def _draw_symbol(pos: ImVec2, size: ImVec2, symbol: _SymbolDrawing, reduce_size_factor: float = 0.6) -> None:
    xc = pos.x + size.x / 2
    yc = pos.y + size.y / 2
    w = size.x / 2 * reduce_size_factor
    h = size.y / 2 * reduce_size_factor

    _draw_symbol_impl(xc - w, yc - h, xc + w, yc + h, symbol)


class ButtonRangeAction(Enum):
    NONE = 1
    MULTIPLY = 2
    DIVIDE = 3


# Buttons to change the range
def show_buttons_range(tooltip_mul: str, tooltip_div: str) -> ButtonRangeAction:
    r = ButtonRangeAction.NONE
    from fiatlight.fiat_widgets import fiat_osd

    orig_cursor_pos = imgui.get_cursor_screen_pos()
    cur_pos = copy.copy(orig_cursor_pos)

    btn_size = hello_imgui.em_to_vec2(1.0, 0.65)
    if imgui.button("##x", btn_size):
        r = ButtonRangeAction.MULTIPLY
    _draw_symbol(cur_pos, btn_size, _SymbolDrawing.ArrowUp)
    fiat_osd.set_widget_tooltip(tooltip_mul)
    cur_pos.y += hello_imgui.em_size(0.7)
    imgui.set_cursor_screen_pos(cur_pos)
    if imgui.button("##10-", btn_size):
        r = ButtonRangeAction.DIVIDE
    _draw_symbol(cur_pos, btn_size, _SymbolDrawing.ArrowDown)
    fiat_osd.set_widget_tooltip(tooltip_div)

    final_cursor_pos = orig_cursor_pos
    final_cursor_pos.x += btn_size.x
    imgui.set_cursor_screen_pos(final_cursor_pos)

    return r


def show_symbol_button(symbol: _SymbolDrawing, tooltip: str, w_em: float = 0.9, h_em: float = 0.9) -> bool:
    clicked = False
    from fiatlight.fiat_widgets import fiat_osd

    orig_cursor_pos = imgui.get_cursor_screen_pos()
    btn_pos = copy.copy(orig_cursor_pos)

    btn_pos.y += hello_imgui.em_size((1.1 - h_em) * 1)

    imgui.set_cursor_screen_pos(btn_pos)
    btn_size = hello_imgui.em_to_vec2(w_em, h_em)
    if imgui.button("##0" + str(symbol), btn_size):
        clicked = True
    _draw_symbol(btn_pos, btn_size, symbol)
    fiat_osd.set_widget_tooltip(tooltip)

    final_cursor_pos = orig_cursor_pos
    final_cursor_pos.x += btn_size.x
    imgui.set_cursor_screen_pos(final_cursor_pos)

    return clicked


def show_sign_button() -> bool:
    return show_symbol_button(_SymbolDrawing.Minus, "Change sign")


def show_zero_button() -> bool:
    return show_symbol_button(_SymbolDrawing.Zero, "Set to zero")
