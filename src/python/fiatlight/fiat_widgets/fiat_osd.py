"""fiat_osd: On-screen display widgets for Fiat.

This module provides functions to display on-screen widgets, such as tooltips and popups.
They are rendered after the node editor canvas (with its nodes) was drawn.
This avoids issues with the canvas's zooming feature, which is incompatible with ImGui windows and child windows.
"""

from fiatlight.fiat_types import VoidFunction, BoolFunction
from imgui_bundle import imgui, ImVec2, imgui_node_editor, hello_imgui
from dataclasses import dataclass


# ======================================================================================================================
# OSD TOOLTIP
# ======================================================================================================================
class _OsdTooltip:
    tooltip_str: str | None = None
    tooltip_gui_function: VoidFunction | None = None

    def render(self) -> None:
        if self.tooltip_gui_function is not None:
            window_pos = imgui.get_mouse_pos()
            window_pos.x += hello_imgui.em_size(1)
            window_pos.y += hello_imgui.em_size(1)
            imgui.set_next_window_pos(window_pos, imgui.Cond_.always.value)
            window_flags = (
                imgui.WindowFlags_.no_collapse.value
                | imgui.WindowFlags_.no_title_bar.value
                | imgui.WindowFlags_.always_auto_resize.value
                | imgui.WindowFlags_.no_move.value
            )
            imgui.begin("Tooltip", True, window_flags)
            self.tooltip_gui_function()
            self.tooltip_gui_function = None
            imgui.end()
        elif self.tooltip_str is not None:
            imgui.set_tooltip(self.tooltip_str)
            self.tooltip_str = None

    def set_tooltip_str(self, tooltip_str: str) -> None:
        self.tooltip_str = tooltip_str

    def set_tooltip_gui(self, gui_function: VoidFunction) -> None:
        self.tooltip_gui_function = gui_function


_OSD_TOOLTIP = _OsdTooltip()


def set_tooltip(tooltip: str) -> None:
    _OSD_TOOLTIP.set_tooltip_str(tooltip)


def set_tooltip_gui(gui_function: VoidFunction) -> None:
    _OSD_TOOLTIP.set_tooltip_gui(gui_function)


# ======================================================================================================================
# OSD Detached Windows
# ======================================================================================================================
@dataclass
class _DetachedWindowInfo:
    btn_label: str  # This is the id
    popup_label: str
    location: ImVec2
    gui_function: VoidFunction | BoolFunction
    bool_returned: bool | None = None
    window_flags: int | None = None  # imgui.WindowFlags_
    window_size: ImVec2 | None = None


class _OsdDetachedWindows:
    """Private data for OSD widgets."""

    detached_windows: list[_DetachedWindowInfo]

    def __init__(self) -> None:
        self.tooltip_str = None
        self.detail_gui = None
        self.detached_windows = []

    def _render_detached_windows(self) -> None:
        alive_windows = []  # remove windows that are closed
        for detached_info in self.detached_windows:
            window_flags = imgui.WindowFlags_.no_collapse.value
            if detached_info.window_flags is not None:
                window_flags |= detached_info.window_flags

            window_size = hello_imgui.em_to_vec2(40, 30)
            if detached_info.window_size is not None:
                window_size = detached_info.window_size

            imgui.set_next_window_pos(detached_info.location, imgui.Cond_.once.value)
            imgui.set_next_window_size(window_size, imgui.Cond_.once.value)
            show, flag_open = imgui.begin(detached_info.popup_label, True, window_flags)
            if show and flag_open:
                detached_info.bool_returned = detached_info.gui_function()
                shall_close = imgui.button("Close")
                if not shall_close:
                    alive_windows.append(detached_info)
            imgui.end()
        self.detached_windows = alive_windows

    def render(self) -> None:
        self._render_detached_windows()

    @staticmethod
    def _detached_window_unique_name(trigger_btn_label: str) -> str:
        return trigger_btn_label + "##" + str(imgui.get_id("BLAH"))

    def _remove_detached_window(self, trigger_btn_label: str) -> None:
        unique_name = self._detached_window_unique_name(trigger_btn_label)
        new_windows = []
        for window in self.detached_windows:
            if window.btn_label != unique_name:
                new_windows.append(window)
        self.detached_windows = new_windows

    def detached_window_exists(self, trigger_btn_label: str) -> bool:
        unique_name = self._detached_window_unique_name(trigger_btn_label)
        for popup_info in self.detached_windows:
            if popup_info.btn_label == unique_name:
                return True
        return False

    def get_detached_window_bool_return(self, trigger_btn_label: str) -> bool | None:
        if not self.detached_window_exists(trigger_btn_label):
            return False
        unique_name = self._detached_window_unique_name(trigger_btn_label)
        for window_info in self.detached_windows:
            if window_info.btn_label == unique_name:
                if not isinstance(window_info.bool_returned, bool):
                    raise ValueError(f"Popup '{trigger_btn_label}' does not return a bool.")
                return window_info.bool_returned
        return False

    def _add_detached_window(
        self,
        trigger_btn_label: str,
        window_label: str,
        gui_function: VoidFunction | BoolFunction,
        bool_returned: bool | None,
        window_flags: int | None,  # imgui.WindowFlags_
        window_size: ImVec2 | None,
    ) -> None:
        if self.detached_window_exists(trigger_btn_label):
            return
        unique_name = self._detached_window_unique_name(trigger_btn_label)
        location = imgui_node_editor.canvas_to_screen(imgui.get_cursor_pos())
        new_popup = _DetachedWindowInfo(
            unique_name, window_label, location, gui_function, bool_returned, window_flags, window_size
        )
        self.detached_windows.append(new_popup)

    def _add_trigger_button(
        self,
        trigger_btn_label: str,
        window_label: str,
        gui_function: VoidFunction | BoolFunction,
        bool_returned: bool | None,
        window_flags: int | None,  # imgui.WindowFlags_
        window_size: ImVec2 | None,
    ) -> None:
        from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6

        tooltip_btn_label = trigger_btn_label
        if "##" in trigger_btn_label:
            tooltip_btn_label = trigger_btn_label.split("##")[0]

        with fontawesome_6_ctx():
            if self.detached_window_exists(trigger_btn_label):
                if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_XMARK + " " + trigger_btn_label):
                    self._remove_detached_window(trigger_btn_label)
                if imgui.is_item_hovered():
                    set_tooltip("Hide " + tooltip_btn_label + " - " + window_label)
            else:
                if imgui.button(icons_fontawesome_6.ICON_FA_MAGNIFYING_GLASS_ARROW_RIGHT + " " + trigger_btn_label):
                    self._add_detached_window(
                        trigger_btn_label, window_label, gui_function, bool_returned, window_flags, window_size
                    )
                if imgui.is_item_hovered():
                    set_tooltip("Show " + tooltip_btn_label + " - " + window_label)

    def update_detached_window_callback(
        self, trigger_btn_label: str, gui_function: BoolFunction | VoidFunction
    ) -> None:
        unique_name = self._detached_window_unique_name(trigger_btn_label)
        for popup_info in self.detached_windows:
            if popup_info.btn_label == unique_name:
                popup_info.gui_function = gui_function

    def show_bool_detached_window_button(
        self,
        trigger_btn_label: str,
        window_label: str,
        gui_function: BoolFunction,
        window_flags: int | None = None,  # imgui.WindowFlags_
        window_size: ImVec2 | None = None,
    ) -> None:
        self._add_trigger_button(trigger_btn_label, window_label, gui_function, False, window_flags, window_size)

    def show_void_detached_window_button(
        self,
        btn_label: str,
        popup_label: str,
        gui_function: VoidFunction,
        window_flags: int | None = None,  # imgui.WindowFlags_
        window_size: ImVec2 | None = None,
    ) -> None:
        self._add_trigger_button(btn_label, popup_label, gui_function, None, window_flags, window_size)


_OSD_DETACHED_WINDOWS = _OsdDetachedWindows()


def show_bool_detached_window_button(
    trigger_btn_label: str,
    window_label: str,
    gui_function: BoolFunction,
    window_flags: int | None = None,  # imgui.WindowFlags_
    window_size: ImVec2 | None = None,
) -> None:
    """Show a button that opens a popup when clicked. The popup contains a boolean function that returns a bool.
    trigger_btn_label: The label of the button.
    window_label: The label of the popup window
    """
    _OSD_DETACHED_WINDOWS.show_bool_detached_window_button(
        trigger_btn_label, window_label, gui_function, window_flags, window_size
    )


def show_void_detached_window_button(
    trigger_btn_label: str,
    window_label: str,
    gui_function: VoidFunction,
    window_flags: int | None = None,  # imgui.WindowFlags_
    window_size: ImVec2 | None = None,
) -> None:
    """Show a button that opens a popup when clicked. The popup contains a void function.
    trigger_btn_label: The label of the button.
    window_label: The label of the popup window
    """
    _OSD_DETACHED_WINDOWS.show_void_detached_window_button(
        trigger_btn_label, window_label, gui_function, window_flags, window_size
    )


def get_detached_window_bool_return(trigger_btn_label: str) -> bool | None:
    """Get the return value of the boolean function in the popup window opened by the button."""
    r = _OSD_DETACHED_WINDOWS.get_detached_window_bool_return(trigger_btn_label)
    return r


def is_detached_window_opened(trigger_btn_label: str) -> bool:
    """Check if a popup window is open."""
    return _OSD_DETACHED_WINDOWS.detached_window_exists(trigger_btn_label)


def update_detached_window_callback(trigger_btn_label: str, gui_function: BoolFunction | VoidFunction) -> None:
    _OSD_DETACHED_WINDOWS.update_detached_window_callback(trigger_btn_label, gui_function)


# ======================================================================================================================
# Global render
# ======================================================================================================================


def _render_all_osd() -> None:
    """Render OSD widgets. Call this once per frame, outside the node editor & nodes."""
    _OSD_TOOLTIP.render()
    _OSD_DETACHED_WINDOWS.render()
