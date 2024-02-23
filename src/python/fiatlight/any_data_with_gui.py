from fiatlight.fiatlight_types import BoolFunction, VoidFunction
from typing import Optional, Any, final


class AnyDataWithGui:
    """
    Override this class with your types, and implement a draw function that presents it content
    """

    value: Any = None

    # Set if needed by implementing a draw function that presents the data content
    gui_present_impl: VoidFunction | None = None

    # Set if needed by implementing a draw function that presents an edit interface for the data
    # and returns True if the data was changed
    gui_edit_impl: BoolFunction | None = None

    def __init__(
        self, value: Any = None, gui_present: Optional[VoidFunction] = None, gui_edit: Optional[BoolFunction] = None
    ) -> None:
        self.value = value
        self.gui_present_impl = gui_present
        self.gui_edit_impl = gui_edit

    @final
    def call_gui_present(self) -> None:
        if self.gui_present_impl is not None:
            self.gui_present_impl()

    @final
    def call_gui_edit(self) -> bool:
        if self.gui_edit_impl is not None:
            return self.gui_edit_impl()
        return False

    def set(self, v: Any) -> None:
        """Override this if you want to add more behavior when setting the value"""
        self.value = v

    def get(self) -> Optional[Any]:
        return self.value
