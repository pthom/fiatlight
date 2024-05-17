"""
This module provides a class to wrap any data with a GUI (AnyDataWithGui), and a class to wrap a named data with a GUI.
See example implementation for a custom type at the bottom of this file.
"""

from fiatlight.fiat_types.base_types import (
    JsonDict,
    DataType,
)
from fiatlight.fiat_types.error_types import Error, ErrorValue, Unspecified, UnspecifiedValue
from fiatlight.fiat_types.function_types import DataPresentFunction, DataEditFunction  # noqa
from fiatlight.fiat_core.any_data_gui_callbacks import AnyDataGuiCallbacks
from typing import Generic, Any, Type, final
import logging


class AnyDataWithGui(Generic[DataType]):
    """
    Instantiate this class with your types, and provide custom functions.
    See example implementation for a custom type at the bottom of this file.
    """

    # ------------------------------------------------------------------------------------------------------------------
    #            Members
    # ------------------------------------------------------------------------------------------------------------------
    # The type of the data
    _type: Type[DataType]

    # The value of the data - can be a DataType, Unspecified, or Error
    # It is accessed through the value property, which triggers the on_change callback (if set)
    _value: DataType | Unspecified | Error = UnspecifiedValue

    # Callbacks for the GUI
    # This is the heart of FiatLight: the GUI is defined by the callbacks.
    # Think of them as __dunder__ methods for the GUI.
    callbacks: AnyDataGuiCallbacks[DataType]

    # If True, the value can be None. This is useful when the data is optional.
    # Otherwise, any None value will be considered as an Error.
    # Note: when using Optional[any registered type], this flag is automatically set to True.
    can_be_none: bool = False

    # Custom attributes that can be set by the user, to give hints to the GUI.
    # For example, with this declaration,
    #         def f(x: int, y: int) -> int:
    #             return x + y
    #        f.x__range = (0, 10)
    # _custom_attrs["range"] will be (0, 10) for the parameter x.
    _custom_attrs: dict[str, Any]

    # ------------------------------------------------------------------------------------------------------------------
    #            Initialization
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, data_type: Type[DataType]) -> None:
        self._type = data_type
        self.callbacks = AnyDataGuiCallbacks.no_handlers()
        self._custom_attrs = {}

    @staticmethod
    def make_for_any() -> "AnyDataWithGui[Any]":
        r = AnyDataWithGui[Any](type(Any))
        return r

    # ------------------------------------------------------------------------------------------------------------------
    #            Value getter and setter + get_actual_value (which returns a DataType or raises an exception)
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def value(self) -> DataType | Unspecified | Error:
        return self._value

    @value.setter
    def value(self, new_value: DataType | Unspecified | Error) -> None:
        self._value = new_value
        if not isinstance(new_value, (Unspecified, Error)):
            if self.callbacks.on_change is not None:
                self.callbacks.on_change(new_value)

    def get_actual_value(self) -> DataType:
        """Returns the actual value of the data, or raises an exception if the value is Unspecified or Error.
        When we are inside a callback, we can be sure that the value is of the correct type, so we can call this method
        instead of accessing the value directly and checking for Unspecified or Error.
        """
        if isinstance(self.value, Unspecified):
            raise ValueError("Cannot get value of Unspecified")
        elif isinstance(self.value, Error):
            raise ValueError("Cannot get value of Error")
        else:
            return self.value

    # ------------------------------------------------------------------------------------------------------------------
    #            Callback utility functions: add callbacks from free functions
    # ------------------------------------------------------------------------------------------------------------------
    def set_edit_callback(self, edit_callback: DataEditFunction[DataType]) -> None:
        self.callbacks.edit = edit_callback

    def set_present_custom_callback(
        self, present_callback: DataPresentFunction[DataType], present_custom_popup_required: bool | None = None
    ) -> None:
        self.callbacks.present_custom = present_callback
        if present_custom_popup_required is not None:
            self.callbacks.present_custom_popup_required = present_custom_popup_required

    # ------------------------------------------------------------------------------------------------------------------
    #            Serialization and deserialization
    # ------------------------------------------------------------------------------------------------------------------
    @final
    def save_to_dict(self, value: DataType | Unspecified | Error) -> JsonDict:
        if isinstance(value, Unspecified):
            return {"type": "Unspecified"}
        elif isinstance(value, Error):
            return {"type": "Error"}
        elif self.callbacks.save_to_dict is not None:
            return self.callbacks.save_to_dict(value)
        elif isinstance(value, (str, int, float, bool)):
            return {"type": "Primitive", "value": value}
        elif isinstance(value, tuple):
            return {"type": "Tuple", "value": value}
        else:
            logging.warning(f"Cannot serialize {value}")
            return {"type": "Error"}

    @final
    def load_from_dict(self, json_data: JsonDict) -> DataType | Unspecified | Error:
        if "type" not in json_data:
            raise ValueError(f"Cannot deserialize {json_data}")
        if json_data["type"] == "Unspecified":
            return UnspecifiedValue
        elif json_data["type"] == "Error":
            return ErrorValue
        elif self.callbacks.load_from_dict is not None:
            return self.callbacks.load_from_dict(json_data)
        elif json_data["type"] == "Primitive":
            r = json_data["value"]
            assert isinstance(r, (str, int, float, bool))
            return r  # type: ignore
        elif json_data["type"] == "Tuple":
            as_list = json_data["value"]
            return tuple(as_list)  # type: ignore
        else:
            raise ValueError(f"Cannot deserialize {json_data}")

    # ------------------------------------------------------------------------------------------------------------------
    #            Utilities
    # ------------------------------------------------------------------------------------------------------------------
    def datatype_value_to_str(self, value: DataType) -> str:
        default_str: str
        if self.callbacks.present_str is not None:
            default_str = self.callbacks.present_str(value)
        else:
            try:
                default_str = str(value)
            except (TypeError, OverflowError):
                default_str = "???"
        return default_str

    def datatype_value_to_clipboard_str(self) -> str:
        if isinstance(self.value, Unspecified):
            return "Unspecified"
        elif isinstance(self.value, Error):
            return "Error"
        else:
            actual_value = self.get_actual_value()
            if self.callbacks.clipboard_copy_str is not None:
                return self.callbacks.clipboard_copy_str(actual_value)
            else:
                return self.datatype_value_to_str(actual_value)

    def can_present_custom(self) -> bool:
        if isinstance(self.value, (Error, Unspecified)):
            return False
        return self.callbacks.present_custom is not None
