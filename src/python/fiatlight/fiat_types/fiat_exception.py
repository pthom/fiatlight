from imgui_bundle import imgui
import logging


class FiatException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class FiatDisplayedException(FiatException):
    """Exception that is displayed to the user in a window."""

    was_dismissed: bool = False
    _popup_id: str
    _was_opened: bool = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self._popup_id = "Error ##" + str(id(self))

    def gui_display(self) -> None:
        if not self._was_opened:
            imgui.open_popup(self._popup_id)
            self._was_opened = True
        try:
            if imgui.begin_popup_modal(self._popup_id):
                imgui.text(self.message)
                if imgui.button("OK"):
                    self.was_dismissed = True
                imgui.end_popup()
            else:
                self.was_dismissed = True
        except Exception as e:
            logging.warning(
                f"""
                Error displaying exception dialog for exception: {self.message}

                Reason: {e}
                        (this is an internal error of fiatlight that needs to be fixed)
            """
            )
            self.was_dismissed = True
