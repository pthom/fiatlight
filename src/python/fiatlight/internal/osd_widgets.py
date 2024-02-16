from imgui_bundle import imgui
from typing import Callable


VoidFunc = Callable[[], None]


#
#
# def _chain_void_functions(f1: VoidFunc|None, f2: VoidFunc|None) -> VoidFunc:
#     def new_void_function() -> None:
#         if f1 is not None:
#             f1()
#         if f2 is not None:
#             f2()
#     return new_void_function


class OsdWidgetsData:
    tooltip: str | None = None
    detail_gui: VoidFunc | None = None


_osd_widgets_data = OsdWidgetsData()


def set_tooltip(tooltip: str) -> None:
    _osd_widgets_data.tooltip = tooltip


def render() -> None:
    if _osd_widgets_data.tooltip is not None:
        imgui.set_tooltip(_osd_widgets_data.tooltip)
        _osd_widgets_data.tooltip = None


def set_detail_gui(detail_gui: VoidFunc) -> None:
    _osd_widgets_data.detail_gui = detail_gui


def get_detail_gui() -> VoidFunc | None:
    return _osd_widgets_data.detail_gui
