import logging

from imgui_bundle import imgui, ImVec2
from fiatlight.fiat_types.function_types import VoidFunction
from typing import Dict


WidgetId = int

_RESIZING_STATE: Dict[WidgetId, bool] = {}


def _is_resizing(widget_id: WidgetId) -> bool:
    if widget_id not in _RESIZING_STATE:
        _RESIZING_STATE[widget_id] = False
    return _RESIZING_STATE[widget_id]


def _set_resizing(widget_id: WidgetId, value: bool) -> None:
    _RESIZING_STATE[widget_id] = value


def widget_with_resize_handle(widget_function: VoidFunction, handle_size_em: float = 1) -> ImVec2:
    widget_function()
    widget_size = imgui.get_item_rect_size()
    widget_id = imgui.get_item_id()

    widget_bottom_right = imgui.get_item_rect_max()
    em = imgui.get_font_size()
    size = em * handle_size_em
    br = ImVec2(widget_bottom_right.x, widget_bottom_right.y)
    bl = ImVec2(br.x - size, br.y)
    tr = ImVec2(br.x, br.y - size)
    tl = ImVec2(br.x - size, br.y - size)

    zone = imgui.internal.ImRect(tl, br)
    color = imgui.Col_.button.value
    if imgui.is_mouse_hovering_rect(zone.min, zone.max):
        color = imgui.Col_.button_hovered.value
    if _is_resizing(widget_id):
        color = imgui.Col_.button_active.value

    imgui.get_window_draw_list().add_triangle_filled(br, bl, tr, imgui.get_color_u32(color))

    if not _is_resizing(widget_id):
        if imgui.is_mouse_hovering_rect(zone.min, zone.max) and imgui.is_mouse_down(0):
            logging.info("Start resizing")
            imgui.set_mouse_cursor(imgui.MouseCursor_.resize_nwse.value)
            _set_resizing(widget_id, True)
    if _is_resizing(widget_id):
        if imgui.is_mouse_down(0):
            drag_delta = imgui.get_mouse_drag_delta(0)
            if drag_delta.x != 0.0 or drag_delta.y != 0.0:
                logging.info(f"Resizing delta: {drag_delta}")
                widget_size.x += drag_delta.x
                widget_size.y += drag_delta.y
                imgui.reset_mouse_drag_delta(0)
        else:
            imgui.set_mouse_cursor(imgui.MouseCursor_.arrow.value)
            _set_resizing(widget_id, False)
            logging.info("Stop resizing")

    return widget_size


def sandbox() -> None:
    from imgui_bundle import immapp, implot
    import numpy as np

    x = np.arange(0, 10, 0.01)
    y = np.sin(x)

    widget_size = ImVec2(200, 200)

    def gui() -> None:
        nonlocal widget_size

        def my_widget() -> None:
            nonlocal widget_size
            if implot.begin_plot("My Plot", widget_size):
                implot.plot_line("My Line", x, y)
                implot.end_plot()

        widget_size = widget_with_resize_handle(my_widget)

    immapp.run(gui, with_implot=True)


if __name__ == "__main__":
    sandbox()
