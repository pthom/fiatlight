from fiatlight.fiat_types import VoidFunction, BoolFunction
from imgui_bundle import imgui, ImVec2, imgui_node_editor
from dataclasses import dataclass


@dataclass
class _PopupInfo:
    name: str
    location: ImVec2
    gui_function: VoidFunction | BoolFunction
    bool_returned: bool | None = None


class _OsdWidgets:
    """Private data for OSD widgets."""

    tooltip: str | None = None
    popups: list[_PopupInfo]
    popups_to_open: list[str]

    def __init__(self) -> None:
        self.tooltip = None
        self.detail_gui = None
        self.popups = []
        self.popups_to_open = []

    def _render_tooltip(self) -> None:
        if self.tooltip is not None:
            imgui.set_tooltip(self.tooltip)
            self.tooltip = None

    def _popup_render(self) -> None:
        # open popups
        for name in self.popups_to_open:
            imgui.open_popup(name)
        self.popups_to_open = []

        # show popups
        new_popups = []
        for popup_info in self.popups:
            imgui.set_next_window_pos(popup_info.location)
            if imgui.begin_popup(popup_info.name):
                popup_info.bool_returned = popup_info.gui_function()
                imgui.end_popup()
                new_popups.append(popup_info)
        self.popups = new_popups

    def render(self) -> None:
        self._render_tooltip()
        self._popup_render()

    def _popup_unique_name(self, name: str) -> str:
        return name + "##" + str(imgui.get_id("BLAH"))

    def get_popup_bool_return(self, name: str) -> bool | None:
        unique_name = self._popup_unique_name(name)
        for popup_info in self.popups:
            if popup_info.name == unique_name:
                if not isinstance(popup_info.bool_returned, bool):
                    raise ValueError(f"Popup '{name}' does not return a bool.")
                return popup_info.bool_returned
        return False

    def add_popup(self, name: str, gui_function: VoidFunction) -> None:
        unique_name = self._popup_unique_name(name)
        location = imgui_node_editor.canvas_to_screen(imgui.get_cursor_pos())
        self.popups.append(_PopupInfo(unique_name, location, gui_function))
        self.popups_to_open.append(unique_name)

    def add_bool_popup(self, name: str, gui_function: BoolFunction) -> None:
        unique_name = self._popup_unique_name(name)
        location = imgui_node_editor.canvas_to_screen(imgui.get_cursor_pos())
        self.popups.append(_PopupInfo(unique_name, location, gui_function, bool_returned=False))
        self.popups_to_open.append(unique_name)


_OSD_WIDGETS = _OsdWidgets()


def set_tooltip(tooltip: str) -> None:
    _OSD_WIDGETS.tooltip = tooltip


def add_popup(name: str, gui_function: VoidFunction) -> None:
    _OSD_WIDGETS.add_popup(name, gui_function)


def add_bool_popup(name: str, gui_function: BoolFunction) -> None:
    _OSD_WIDGETS.add_bool_popup(name, gui_function)


def get_popup_bool_return(name: str) -> bool | None:
    r = _OSD_WIDGETS.get_popup_bool_return(name)
    return r


def render() -> None:
    """Render OSD widgets. Call this once per frame, outside the node editor & nodes."""
    _OSD_WIDGETS.render()
