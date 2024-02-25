from fiatlight.fiatlight_types import BoolFunction, VoidFunction
from typing import Optional, Any, final, Callable, TypeAlias
import json

DataType: TypeAlias = Any


class AnyDataWithGui:
    """
    Instantiate this class with your types, and provide draw functions that presents it content
    """

    # The value of the data
    value: DataType = None

    # Provide a draw function that presents the data content
    gui_present_impl: VoidFunction | None = None

    # Provide a draw function that presents an editable interface for the data, and returns True if changed
    gui_edit_impl: BoolFunction | None = None

    # Optional serialization and deserialization functions for DataType
    # If provided, these functions will be used to serialize and deserialize the data with a custom dict format.
    # If not provided, "value" will be serialized as a dict of its __dict__ attribute,
    # or as a json string (for int, float, str, bool, and None)
    to_dict: Callable[[DataType], dict[str, Any]] | None = None
    from_dict: Callable[[dict[str, Any]], DataType] | None = None

    def _has_custom_serialization(self) -> bool:
        return self.to_dict is not None and self.from_dict is not None

    def to_json(self) -> str:
        if self.value is None:
            return "null"
        elif isinstance(self.value, (str, int, float, bool)):
            return json.dumps(self.value)
        elif self._has_custom_serialization():
            assert self.to_dict is not None
            as_dict = self.to_dict(self.value)
            return json.dumps(as_dict)
        elif hasattr(self.value, "__dict__"):
            as_dict = self.value.__dict__
            return json.dumps(as_dict)
        else:
            raise ValueError(f"Cannot serialize {self.value}, it has no __dict__ attribute.")

    def from_json(self, json_str: str) -> None:
        if json_str == "null":
            self.value = None
        else:
            as_dict_or_value = json.loads(json_str)
            if isinstance(as_dict_or_value, (str, int, float, bool)):
                self.value = as_dict_or_value
            else:
                as_dict = as_dict_or_value
                if self._has_custom_serialization():
                    assert self.from_dict is not None
                    self.value = self.from_dict(as_dict)
                else:
                    # Ouch, what if value is None?
                    # We need a way to know the type of the value, or to have a default value
                    self.value.__dict__.update(as_dict)

    def __init__(
        self,
        value: DataType = None,
        gui_present: Optional[VoidFunction] = None,
        gui_edit: Optional[BoolFunction] = None,
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
