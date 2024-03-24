from fiatlight.fiat_types import VoidFunction, BoolFunction
from imgui_bundle import imgui, ImVec2, imgui_node_editor, hello_imgui
from dataclasses import dataclass


@dataclass
class _PopupInfo:
    btn_label: str  # This is the id
    popup_label: str
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
        alive_popups = []  # remove popups that are closed
        for popup_info in self.popups:
            window_flags = imgui.WindowFlags_.no_collapse.value
            imgui.set_next_window_pos(popup_info.location, imgui.Cond_.appearing.value)
            imgui.set_next_window_size(hello_imgui.em_to_vec2(40, 15), imgui.Cond_.appearing.value)
            show, flag_open = imgui.begin(popup_info.popup_label, True, window_flags)
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

    def _popup_unique_name(self, popup_label: str) -> str:
        return popup_label + "##" + str(imgui.get_id("BLAH"))

    def _remove_popup(self, popup_label: str) -> None:
        unique_name = self._popup_unique_name(popup_label)
        new_popups = []
        for popup_info in self.popups:
            if popup_info.btn_label != unique_name:
                new_popups.append(popup_info)
        self.popups = new_popups

    def _popup_exists(self, popup_label: str) -> bool:
        unique_name = self._popup_unique_name(popup_label)
        for popup_info in self.popups:
            if popup_info.btn_label == unique_name:
                return True
        return False

    def get_popup_bool_return(self, btn_label: str) -> bool | None:
        if not self._popup_exists(btn_label):
            return False
        unique_name = self._popup_unique_name(btn_label)
        for popup_info in self.popups:
            if popup_info.btn_label == unique_name:
                if not isinstance(popup_info.bool_returned, bool):
                    raise ValueError(f"Popup '{btn_label}' does not return a bool.")
                return popup_info.bool_returned
        return False

    def _add_popup(
        self,
        btn_label: str,
        popup_label: str,
        gui_function: VoidFunction | BoolFunction,
        bool_returned: bool | None,
    ) -> None:
        if self._popup_exists(btn_label):
            return
        unique_name = self._popup_unique_name(btn_label)
        location = imgui_node_editor.canvas_to_screen(imgui.get_cursor_pos())
        self.popups.append(_PopupInfo(unique_name, popup_label, location, gui_function, bool_returned))

    def _add_popup_button(
        self, btn_label: str, popup_label: str, gui_function: VoidFunction | BoolFunction, bool_returned: bool | None
    ) -> None:
        from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6

        with fontawesome_6_ctx():
            if self._popup_exists(btn_label):
                if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_XMARK + " " + btn_label):
                    self._remove_popup(btn_label)
                if imgui.is_item_hovered():
                    self.tooltip = "Hide " + btn_label + " - " + popup_label
            else:
                # if imgui.button(icons_fontawesome_6.ICON_FA_EYE + " " + btn_label):
                if imgui.button(icons_fontawesome_6.ICON_FA_MAGNIFYING_GLASS_ARROW_RIGHT + " " + btn_label):
                    self._add_popup(btn_label, popup_label, gui_function, bool_returned)
                if imgui.is_item_hovered():
                    self.tooltip = "Show " + btn_label + " - " + popup_label

    def show_bool_popup_button(self, btn_label: str, popup_label: str, gui_function: BoolFunction) -> None:
        self._add_popup_button(btn_label, popup_label, gui_function, False)

    def show_void_popup_button(self, btn_label: str, popup_label: str, gui_function: VoidFunction) -> None:
        self._add_popup_button(btn_label, popup_label, gui_function, None)


_OSD_WIDGETS = _OsdWidgets()


def set_tooltip(tooltip: str) -> None:
    _OSD_WIDGETS.tooltip = tooltip


def show_bool_popup_button(btn_label: str, popup_label: str, gui_function: BoolFunction) -> None:
    """Show a button that opens a popup when clicked. The popup contains a boolean function that returns a bool.
    btn_label: The label of the button.
    popup_label: The label of the popup window
    """
    _OSD_WIDGETS.show_bool_popup_button(btn_label, popup_label, gui_function)


def show_void_popup_button(btn_label: str, popup_label: str, gui_function: VoidFunction) -> None:
    """Show a button that opens a popup when clicked. The popup contains a void function.
    btn_label: The label of the button.
    popup_label: The label of the popup window
    """
    _OSD_WIDGETS.show_void_popup_button(btn_label, popup_label, gui_function)


def get_popup_bool_return(btn_label: str) -> bool | None:
    """Get the return value of the boolean function in the popup window opened by the button."""
    r = _OSD_WIDGETS.get_popup_bool_return(btn_label)
    return r


def render() -> None:
    """Render OSD widgets. Call this once per frame, outside the node editor & nodes."""
    _OSD_WIDGETS.render()
