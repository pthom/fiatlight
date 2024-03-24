"""
This module provides a class to wrap any data with a GUI (AnyDataWithGui), and a class to wrap a named data with a GUI.
See example implementation for a custom type at the bottom of this file.
"""
from fiatlight.fiat_types import (
    Error,
    ErrorValue,
    Unspecified,
    UnspecifiedValue,
    JsonDict,
    DataType,
)
from fiatlight.fiat_core.any_data_gui_callbacks import AnyDataGuiCallbacks  # noqa
from typing import Generic, Any
from imgui_bundle import imgui
import logging


class AnyDataWithGui(Generic[DataType]):
    """
    Instantiate this class with your types, and provide draw functions that presents it content.
    See example implementation for a custom type at the bottom of this file.
    """

    # The value of the data - can be a DataType, Unspecified, or Error
    _value: DataType | Unspecified | Error = UnspecifiedValue

    # Handlers
    callbacks: AnyDataGuiCallbacks[DataType]

    def __init__(self) -> None:
        self.callbacks = AnyDataGuiCallbacks.no_handlers()

    @staticmethod
    def from_handlers(handlers: AnyDataGuiCallbacks[DataType]) -> "AnyDataWithGui[DataType]":
        r: AnyDataWithGui[DataType] = AnyDataWithGui()
        r.callbacks = handlers
        return r

    @staticmethod
    def make_default() -> "AnyDataWithGui[Any]":
        return AnyDataWithGui()

    @property
    def value(self) -> DataType | Unspecified | Error:
        return self._value

    @value.setter
    def value(self, new_value: DataType | Unspecified | Error) -> None:
        self._value = new_value
        if self.callbacks.on_change is not None and isinstance(new_value, (Unspecified, Error)) is False:
            self.callbacks.on_change()

    def get_actual_value(self) -> DataType:
        if isinstance(self.value, Unspecified):
            raise ValueError("Cannot get value of Unspecified")
        elif isinstance(self.value, Error):
            raise ValueError("Cannot get value of Error")
        else:
            return self.value

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

    def can_present_value(self) -> bool:
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
    def edit(self) -> bool:
        assert isinstance(self.value, Foo)
        changed, self.value.x = imgui.input_int("x", self.value.x)
        return changed

    @staticmethod
    def present_str(value: Foo) -> str:
        return f"Foo: x={value.x}"


def test_foo_with_gui() -> None:
    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.fiat_core.to_gui import to_data_with_gui, gui_factories

    gui_factories().add_factory("Foo", FooWithGui)

    foo = Foo(1)
    foo_gui = to_data_with_gui(foo)
    assert foo_gui.value == foo


if __name__ == "__main__":
    test_foo_with_gui()
