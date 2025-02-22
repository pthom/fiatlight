from imgui_bundle import imgui
from typing import Generic
from typing import TypeVar

DataType = TypeVar("DataType")


class ValuePerImGuiFrame(Generic[DataType]):
    """A value that is stored per ImGui frame, i.e. it is reset at the beginning of each frame."""

    value: DataType | None = None
    last_frame: int = -1

    def __init__(self) -> None:
        pass

    def get(self) -> DataType | None:
        """Retrieve the value for the current ImGui frame, or return None."""
        current_frame = imgui.get_frame_count()
        if current_frame != self.last_frame:
            self.value = None
        return self.value

    def set(self, value: DataType) -> None:
        """Set the value for the current ImGui frame."""
        self.value = value
        self.last_frame = imgui.get_frame_count()
