from typing import Optional, Any
from imgui_bundle import imgui


class AnyDataWithGui:
    """
    Override this class with your types, and implement a draw function that presents it content
    """

    value: Any = None

    def gui_present(self) -> None:
        """Override this if needed by implementing a draw function that presents the data content"""
        imgui.text(f"{self.value}")

    def set(self, v: Any) -> None:
        """Override this if you want to add more behavior when setting the value"""
        self.value = v

    def get(self) -> Optional[Any]:
        return self.value
