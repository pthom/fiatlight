from imgui_bundle import imgui


class FiatException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class FiatDisplayedException(FiatException):
    """Exception that is displayed to the user in a window."""

    popup_id: str
    was_dismissed: bool = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.popup_id = "Error ##" + str(id(self))
        imgui.open_popup(self.popup_id)

    def gui_display(self) -> None:
        if imgui.begin_popup_modal(self.popup_id):
            imgui.text(self.message)
            if imgui.button("OK"):
                self.was_dismissed = True
            imgui.end_popup()
        else:
            self.was_dismissed = True
