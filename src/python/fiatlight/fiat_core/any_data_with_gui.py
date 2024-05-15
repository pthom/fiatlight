"""
This module provides a class to wrap any data with a GUI (AnyDataWithGui), and a class to wrap a named data with a GUI.
See example implementation for a custom type at the bottom of this file.
"""
from enum import Enum

from fiatlight.fiat_types.base_types import (
    JsonDict,
    DataType,
)
from fiatlight.fiat_types.error_types import Error, ErrorValue, Unspecified, UnspecifiedValue
from fiatlight.fiat_types.function_types import DataPresentFunction, DataEditFunction  # noqa
from fiatlight.fiat_core.any_data_gui_callbacks import AnyDataGuiCallbacks
from typing import Generic, Any
from imgui_bundle import imgui
import logging


class AnyDataWithGui(Generic[DataType]):
    """
    Instantiate this class with your types, and provide custom functions.
    See example implementation for a custom type at the bottom of this file.
    """

    # ------------------------------------------------------------------------------------------------------------------
    #            Members
    # ------------------------------------------------------------------------------------------------------------------
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
    def __init__(self) -> None:
        self.callbacks = AnyDataGuiCallbacks.no_handlers()
        self._custom_attrs = {}

    @staticmethod
    def make_for_any() -> "AnyDataWithGui[Any]":
        """Creates an AnyDataWithGui with no type specified.
        This is useful when we don't know the type of the data."""
        return AnyDataWithGui()

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
    def save_to_json(self) -> JsonDict:
        if isinstance(self.value, Unspecified):
            return {"type": "Unspecified"}
        elif isinstance(self.value, Error):
            return {"type": "Error"}
        elif isinstance(self.value, (str, int, float, bool)):
            return {"type": "Primitive", "value": self.value}
        elif self.value is None:
            return {"type": "Primitive", "value": None}
        # elif self.callbacks.to_dict_impl is not None:
        #     as_dict = self.callbacks.to_dict_impl(self.value)
        #     return {"type": "Custom", "value": as_dict}
        elif isinstance(self.value, Enum):
            return {"type": "Enum", "value_name": self.value.name, "class": self.value.__class__.__name__}
        elif hasattr(self.value, "__dict__"):
            as_dict = self.value.__dict__
            return {"type": "Dict", "value": as_dict}
        elif isinstance(self.value, list):
            # return {"type": "List", "value": [AnyDataWithGui(x, self.callbacks).to_json() for x in self.value]}
            logging.warning("List serialization not implemented yet")
            return {"type": "List"}
        elif isinstance(self.value, tuple):
            return {"type": "Tuple", "value": self.value}
        else:
            logging.warning(f"Cannot serialize {self.value}, it has no __dict__ attribute.")
            return {"type": "Error"}

    def load_from_json(self, json_data: JsonDict) -> None:
        if "type" not in json_data:
            raise ValueError(f"Cannot deserialize {json_data}")
        if json_data["type"] == "Unspecified":
            self.value = UnspecifiedValue
        elif json_data["type"] == "Error":
            self.value = ErrorValue
        elif json_data["type"] == "Primitive":
            self.value = json_data["value"]
        # elif json_data["type"] == "Custom":
        #     assert self.callbacks.from_dict_impl is not None
        #     self.value = self.callbacks.from_dict_impl(json_data["value"])
        elif json_data["type"] == "Enum":
            if self.callbacks.create_from_value is None:
                raise ValueError("Cannot deserialize an Enum without a create_from_value callback")
            self.value = self.callbacks.create_from_value(json_data["value_name"])

        elif json_data["type"] == "Dict":
            if self.value is UnspecifiedValue:
                if self.callbacks.default_value_provider is None:
                    raise ValueError("Cannot deserialize a None value without a default_value_provider")
                self.value = self.callbacks.default_value_provider()
            self.value.__dict__.update(json_data["value"])
        elif json_data["type"] == "Tuple":
            as_list = json_data["value"]
            self.value = tuple(as_list)  # type: ignore
        elif json_data["type"] == "List":
            logging.warning("List deserialization not implemented yet")
            return
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


##############################################################################################################
# Example implementation for a custom type
##############################################################################################################
class Foo:
    x: int

    def __init__(self, x: int) -> None:
        self.x = x


class FooWithGui(AnyDataWithGui[Foo]):
    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.present_str = self.present_str
        self.callbacks.default_value_provider = lambda: Foo(x=0)

    # Edit and present functions
    def edit(self, value: Foo) -> tuple[bool, Foo]:
        # When edit is called, self.value is guaranteed to be a Foo, so that we can call self.get_actual_value()
        # in order to get the actual value with the correct type.
        changed, value.x = imgui.input_int("x", value.x)
        return changed, value

    @staticmethod
    def present_str(value: Foo) -> str:
        return f"Foo: x={value.x}"


def sandbox() -> None:
    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    import fiatlight

    fiatlight.register_type(Foo, FooWithGui)

    def fn_using_foo(foo: Foo) -> int:
        return foo.x

    fn_using_foo_with_gui = fiatlight.FunctionWithGui(fn_using_foo)
    fn_input_gui = fn_using_foo_with_gui.input("foo")
    assert isinstance(fn_input_gui, FooWithGui)


if __name__ == "__main__":
    sandbox()
