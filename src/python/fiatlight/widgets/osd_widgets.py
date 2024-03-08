from fiatlight.core import VoidFunction
from imgui_bundle import imgui


class OsdWidgetsData:
    tooltip: str | None = None
    detail_gui: VoidFunction | None = None


_osd_widgets_data = OsdWidgetsData()


def set_tooltip(tooltip: str) -> None:
    _osd_widgets_data.tooltip = tooltip


def render() -> None:
    if _osd_widgets_data.tooltip is not None:
        imgui.set_tooltip(_osd_widgets_data.tooltip)
        _osd_widgets_data.tooltip = None


def set_detail_gui(detail_gui: VoidFunction) -> None:
    _osd_widgets_data.detail_gui = detail_gui


def get_detail_gui() -> VoidFunction | None:
    return _osd_widgets_data.detail_gui
