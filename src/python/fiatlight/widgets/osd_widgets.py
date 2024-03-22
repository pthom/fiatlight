from fiatlight.core import VoidFunction
from imgui_bundle import imgui, ImVec2, imgui_node_editor
from dataclasses import dataclass


@dataclass
class _PopupInfo:
    name: str
    gui: VoidFunction
    location: ImVec2


class _OsdWidgets:
    """Private data for OSD widgets."""

    tooltip: str | None = None
    popups: list[_PopupInfo]
    popups_to_open: [str]

    def __init__(self) -> None:
        self.tooltip = None
        self.detail_gui = None
        self.popups = []
        self.popups_to_open = []

    def _render_tooltip(self) -> None:
        if self.tooltip is not None:
            imgui.set_tooltip(self.tooltip)
            self.tooltip = None

    def _render_popups(self) -> None:
        # open popups
        for name in self.popups_to_open:
            imgui.open_popup(name)
        self.popups_to_open = []

        # show popups
        new_popups = []
        for popup_info in self.popups:
            imgui.set_next_window_pos(popup_info.location)
            if imgui.begin_popup(popup_info.name):
                popup_info.gui()
                imgui.end_popup()
                new_popups.append(popup_info)
        self.popups = new_popups

    def render(self) -> None:
        self._render_tooltip()
        self._render_popups()

    def add_popup(self, name: str, gui_function: VoidFunction) -> None:
        name = name + "##" + str(imgui.get_id("BLAH"))  # make unique
        location = imgui_node_editor.canvas_to_screen(imgui.get_cursor_pos())
        self.popups.append(_PopupInfo(name, gui_function, location))
        self.popups_to_open.append(name)


_OSD_WIDGETS = _OsdWidgets()


def set_tooltip(tooltip: str) -> None:
    _OSD_WIDGETS.tooltip = tooltip


def add_popup(name: str, gui_function: VoidFunction) -> None:
    _OSD_WIDGETS.add_popup(name, gui_function)


def render() -> None:
    """Render OSD widgets. Call this once per frame, outside the node editor & nodes."""
    _OSD_WIDGETS.render()
