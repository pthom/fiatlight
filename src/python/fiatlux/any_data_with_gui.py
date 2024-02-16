from typing import Optional, Any
from abc import ABC, abstractmethod


class AnyDataWithGui(ABC):
    """
    Override this class with your types, and implement a draw function that presents it content
    """

    value: Any

    @abstractmethod
    def gui_data(self, function_name: str) -> None:
        """Override this by implementing a draw function that presents the data content"""
        pass

    def gui_set_input(self) -> Optional[Any]:
        """Override this if you want to provide a visual way to set the input of
        a function composition graph"""
        return None

    def set(self, v: Any) -> None:
        """Override this if you want to add more behavior when setting the value"""
        self.value = v

    def get(self) -> Optional[Any]:
        return self.value
