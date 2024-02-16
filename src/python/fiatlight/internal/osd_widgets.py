from imgui_bundle import imgui


class OsdWidgetsData:
    tooltip: str | None = None


_osd_widgets_data = OsdWidgetsData()


def set_tooltip(tooltip: str) -> None:
    _osd_widgets_data.tooltip = tooltip


# def on_new_frame() -> None:
#     _osd_widgets_data.tooltip_text = None


def render() -> None:
    if _osd_widgets_data.tooltip is not None:
        imgui.set_tooltip(_osd_widgets_data.tooltip)
        _osd_widgets_data.tooltip = None
