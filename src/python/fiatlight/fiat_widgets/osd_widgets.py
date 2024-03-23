from fiatlight.fiat_types import VoidFunction, BoolFunction
from imgui_bundle import imgui, ImVec2, imgui_node_editor, hello_imgui
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

    def __init__(self) -> None:
        self.tooltip = None
        self.detail_gui = None
        self.popups = []

    def _render_tooltip(self) -> None:
        if self.tooltip is not None:
            imgui.set_tooltip(self.tooltip)
            self.tooltip = None

    def _popup_render(self) -> None:
        # open popups
        # for name in self.popups_to_open:
        #     imgui.open_popup(name)
        # self.popups_to_open = []

        # show popups
        alive_popups = []  # remove popups that are closed
        for popup_info in self.popups:
            window_flags = imgui.WindowFlags_.no_collapse.value
            imgui.set_next_window_pos(popup_info.location, imgui.Cond_.appearing.value)
            imgui.set_next_window_size(hello_imgui.em_to_vec2(40, 15), imgui.Cond_.appearing.value)
            show, flag_open = imgui.begin(popup_info.name, True, window_flags)
            if show and flag_open:
                popup_info.bool_returned = popup_info.gui_function()
                shall_close = imgui.button("Close")
                if not shall_close:
                    alive_popups.append(popup_info)
            imgui.end()
        self.popups = alive_popups

    def render(self) -> None:
        self._render_tooltip()
        self._popup_render()

    def _popup_unique_name(self, name: str) -> str:
        return name + "##" + str(imgui.get_id("BLAH"))

    def _remove_popup(self, name: str) -> None:
        unique_name = self._popup_unique_name(name)
        new_popups = []
        for popup_info in self.popups:
            if popup_info.name != unique_name:
                new_popups.append(popup_info)
        self.popups = new_popups

    def _popup_present(self, name: str) -> bool:
        unique_name = self._popup_unique_name(name)
        for popup_info in self.popups:
            if popup_info.name == unique_name:
                return True
        return False

    def get_popup_bool_return(self, name: str) -> bool | None:
        if not self._popup_present(name):
            return False
        unique_name = self._popup_unique_name(name)
        for popup_info in self.popups:
            if popup_info.name == unique_name:
                if not isinstance(popup_info.bool_returned, bool):
                    raise ValueError(f"Popup '{name}' does not return a bool.")
                return popup_info.bool_returned
        return False

    def _add_popup(self, name: str, gui_function: VoidFunction | BoolFunction, bool_returned: bool | None) -> None:
        if self._popup_present(name):
            return
        unique_name = self._popup_unique_name(name)
        location = imgui_node_editor.canvas_to_screen(imgui.get_cursor_pos())
        self.popups.append(_PopupInfo(unique_name, location, gui_function, bool_returned))

    def _add_popup_button(
        self, name: str, gui_function: VoidFunction | BoolFunction, bool_returned: bool | None
    ) -> None:
        from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6

        with fontawesome_6_ctx():
            if self._popup_present(name):
                if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_XMARK + " " + name):
                    self._remove_popup(name)
            else:
                if imgui.button(icons_fontawesome_6.ICON_FA_EYE + " " + name):
                    self._add_popup(name, gui_function, bool_returned)

    def add_bool_popup_button(self, name: str, gui_function: BoolFunction) -> None:
        self._add_popup_button(name, gui_function, False)


_OSD_WIDGETS = _OsdWidgets()


def set_tooltip(tooltip: str) -> None:
    _OSD_WIDGETS.tooltip = tooltip


def add_bool_popup_button(name: str, gui_function: BoolFunction) -> None:
    _OSD_WIDGETS.add_bool_popup_button(name, gui_function)


def get_popup_bool_return(name: str) -> bool | None:
    r = _OSD_WIDGETS.get_popup_bool_return(name)
    return r


def render() -> None:
    """Render OSD widgets. Call this once per frame, outside the node editor & nodes."""
    _OSD_WIDGETS.render()
