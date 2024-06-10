"""fiat_osd: On-screen display widgets for Fiat.

This module provides functions to display on-screen widgets, such as tooltips and popups.
They are rendered after the node editor canvas (with its nodes) was drawn.
This avoids issues with the canvas's zooming feature, which is incompatible with ImGui windows and child windows.
"""

from fiatlight.fiat_types import VoidFunction, BoolFunction
from imgui_bundle import imgui, ImVec2, imgui_node_editor, hello_imgui, imgui_ctx, ImVec4
from dataclasses import dataclass


_IS_PRESENTLY_IN_DETACHED_WINDOW = False


def is_rendering_in_node() -> bool:
    """Check if we are currently rendering inside a Node.

    You may want to check this value when implementing `present` or `edit`
    callbacks inside `AnyDataGuiCallbacks` for several possible reasons:

        - Some widgets cannot be presented in a Node (e.g., a multiline text input),
          be can be presented in a detached window.
        - When inside a Node, you may want to render a smaller version, to save space
          (as opposed to rendering a larger version in a detached window).
    """
    if imgui_node_editor.get_current_editor() is None:
        return False
    return not _IS_PRESENTLY_IN_DETACHED_WINDOW


def is_rendering_in_fiatlight_detached_window() -> bool:
    """Check if we are currently rendering inside a regular ImGui window.
    You may want to check this value when implementing `present` or `edit`
    callbacks inside `AnyDataGuiCallbacks` for several possible reasons:

    - Some widgets cannot be presented in a Node (e.g., a multiline text input),
      be can be presented in a detached window.
    - When inside a Node, you may want to render a smaller version, to save space
      (as opposed to rendering a larger version in a detached window).
    """
    if imgui_node_editor.get_current_editor() is None:
        return False
    return _IS_PRESENTLY_IN_DETACHED_WINDOW


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


def set_widget_tooltip(tooltip: str) -> None:
    is_in_editor = imgui_node_editor.get_current_editor() is not None
    if imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal.value):
        if is_in_editor:
            _OSD_TOOLTIP.set_tooltip_str(tooltip)
        else:
            imgui.set_tooltip(tooltip)


def set_tooltip(tooltip: str) -> None:
    _OSD_TOOLTIP.set_tooltip_str(tooltip)


def set_widget_tooltip_gui(gui_function: VoidFunction) -> None:
    if imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal.value):
        _OSD_TOOLTIP.set_tooltip_gui(gui_function)


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
        global _IS_PRESENTLY_IN_DETACHED_WINDOW
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
                _IS_PRESENTLY_IN_DETACHED_WINDOW = True
                detached_info.bool_returned = detached_info.gui_function()
                _IS_PRESENTLY_IN_DETACHED_WINDOW = False
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
                set_widget_tooltip("Hide " + tooltip_btn_label + " - " + window_label)
            else:
                if imgui.button(icons_fontawesome_6.ICON_FA_MAGNIFYING_GLASS_ARROW_RIGHT + " " + trigger_btn_label):
                    self._add_detached_window(
                        trigger_btn_label, window_label, gui_function, bool_returned, window_flags, window_size
                    )
                set_widget_tooltip("Show " + tooltip_btn_label + " - " + window_label)

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
# OSD Popup
# ======================================================================================================================
class _OsdPopup:
    popup_gui_function: VoidFunction | None = None

    _popup_id = "This is our own unique id!"
    _needs_open = False

    def set_popup_gui(self, gui_function: VoidFunction) -> None:
        self.popup_gui_function = gui_function
        self._needs_open = True

    def render(self) -> None:
        if self._needs_open:
            imgui.open_popup(self._popup_id)
            self._needs_open = False
        if self.popup_gui_function is not None:
            if imgui.begin_popup(self._popup_id):
                self.popup_gui_function()
                imgui.end_popup()
            else:
                self.popup_gui_function = None


_OSD_POPUP = _OsdPopup()


def set_popup_gui(gui_function: VoidFunction) -> None:
    _OSD_POPUP.set_popup_gui(gui_function)


# ======================================================================================================================
# OSD Notifications
# ======================================================================================================================
_NOTIF_DURATION = 5.0
_NOTIF_SIZE_EM = ImVec2(22, 4)


class _OsdNotificationData:
    gui: VoidFunction
    start_time: float
    identifier: str

    def __init__(self, gui: VoidFunction, identifier: str) -> None:
        self.gui = gui
        self.identifier = identifier
        self.start_time = imgui.get_time()

    def _alpha_transparency(self) -> float:
        ttl_ratio = self._ttl() / _NOTIF_DURATION
        k = 0.2
        if ttl_ratio > k:
            return 1.0
        return ttl_ratio / k

    def _ttl(self) -> float:
        return _NOTIF_DURATION - (imgui.get_time() - self.start_time)

    def render(self, position: ImVec2) -> None:
        transparency = self._alpha_transparency()
        imgui.set_next_window_pos(position, imgui.Cond_.always.value)
        imgui.set_next_window_bg_alpha(0.5 * transparency)
        size_pixels = hello_imgui.em_to_vec2(_NOTIF_SIZE_EM.x, _NOTIF_SIZE_EM.y)
        imgui.set_next_window_size(size_pixels, imgui.Cond_.always.value)
        flags = (
            imgui.WindowFlags_.no_collapse.value
            | imgui.WindowFlags_.no_title_bar.value
            | imgui.WindowFlags_.no_move.value
            | imgui.WindowFlags_.no_resize.value
            | imgui.WindowFlags_.no_scrollbar.value
            | imgui.WindowFlags_.no_saved_settings.value
            | imgui.WindowFlags_.no_focus_on_appearing.value
        )
        window_label = "##Notification" + self.identifier + str(id(self))
        with imgui_ctx.begin(window_label, False, flags):
            # change text color
            txt_color = imgui.get_style().color_(imgui.Col_.text.value)
            txt_transparent_color = ImVec4(txt_color.x, txt_color.y, txt_color.z, txt_color.w * transparency)
            with imgui_ctx.push_style_color(imgui.Col_.text.value, txt_transparent_color):
                self.gui()

    def shall_close(self) -> bool:
        return imgui.get_time() - self.start_time > _NOTIF_DURATION


class _OsdNotifications:
    """Private data for OSD widgets."""

    notifications: list[_OsdNotificationData]

    def __init__(self) -> None:
        self.notifications = []

    def _render_notifications(self) -> None:
        self._remove_old_notifs()

        # Render notifications
        num_notifications = len(self.notifications)
        if num_notifications == 0:
            return
        window_br_corner = ImVec2(
            imgui.get_window_pos().x + imgui.get_window_size().x, imgui.get_window_pos().y + imgui.get_window_size().y
        )
        notification_width = hello_imgui.em_size(_NOTIF_SIZE_EM.x)
        notification_height = hello_imgui.em_size(_NOTIF_SIZE_EM.y)
        current_window_position = ImVec2(window_br_corner.x - notification_width, window_br_corner.y)
        for notification in self.notifications:
            current_window_position.y -= notification_height
            notification.render(current_window_position)

    def _remove_old_notifs(self) -> None:
        new_notifications = []
        for notification in self.notifications:
            if not notification.shall_close():
                new_notifications.append(notification)
        self.notifications = new_notifications

    def render(self) -> None:
        self._render_notifications()

    def _already_has_notification(self, identifier: str) -> bool:
        for notification in self.notifications:
            if notification.identifier == identifier:
                return True
        return False

    def add_notification_str(self, identifier: str, notification: str) -> None:
        if self._already_has_notification(identifier):
            return

        def gui() -> None:
            imgui.text(notification)

        self.notifications.append(_OsdNotificationData(gui, identifier))

    def add_notification_gui(self, identifier: str, gui_function: VoidFunction) -> None:
        if self._already_has_notification(identifier):
            return
        self.notifications.append(_OsdNotificationData(gui_function, identifier))


_OSD_NOTIFICATIONS = _OsdNotifications()


def add_notification_str(identifier: str, notification: str) -> None:
    _OSD_NOTIFICATIONS.add_notification_str(identifier, notification)


def add_notification_gui(identifier: str, gui_function: VoidFunction) -> None:
    _OSD_NOTIFICATIONS.add_notification_gui(identifier, gui_function)


# ======================================================================================================================
# Global render
# ======================================================================================================================
def _render_all_osd() -> None:
    """Render OSD widgets. Call this once per frame, outside the node editor & nodes."""
    _OSD_TOOLTIP.render()
    _OSD_DETACHED_WINDOWS.render()
    _OSD_POPUP.render()
    _OSD_NOTIFICATIONS.render()
