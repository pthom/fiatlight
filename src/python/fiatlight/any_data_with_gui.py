from imgui_bundle import imgui
from typing import Optional, Any, Callable


PresentFunction = Callable[[Any], None]


class AnyDataWithGui:
    """
    Override this class with your types, and implement a draw function that presents it content
    """

    value: Any = None

    # gui_present: PresentFunction

    def __init__(self, value: Any = None) -> None:
        self.value = value
        # if gui_present is None:
        #     self.gui_present = lambda: _default_gui_present(self.value)
        # else:
        #     self.gui_present = gui_present

    def gui_present(self) -> None:
        """Override this if needed by implementing a draw function that presents the data content"""
        imgui.text(f"{self.value}")

    def gui_edit(self) -> bool:
        """Override this if needed by implementing a gui function that edits the data content
        and returns True if the value was changed"""
        return False

    def set(self, v: Any) -> None:
        """Override this if you want to add more behavior when setting the value"""
        self.value = v

    def get(self) -> Optional[Any]:
        return self.value
