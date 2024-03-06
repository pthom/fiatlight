"""
This module provides a class to wrap any data with a GUI (AnyDataWithGui), and a class to wrap a named data with a GUI.
See example implementation for a custom type at the bottom of this file.
"""
from fiatlight.fiatlight_types import Error, ErrorValue, Unspecified, UnspecifiedValue, JsonDict
from typing import final, Callable, TypeVar, Generic, Tuple
from dataclasses import dataclass
from imgui_bundle import imgui
from fiatlight import IconsFontAwesome6
from enum import Enum
import logging

# DataType: TypeAlias = Any
DataType = TypeVar("DataType")


class AnyDataGuiHandlers(Generic[DataType]):
    """
    Collection of callbacks for a given type
    - edit and present: the GUI implementation of the type
    - to_dict and from_dict: the serialization and deserialization functions (optional)
    - default_value_provider: the function that provides a default value for the type

    See example implementation for a custom type at the bottom of this file.
    """

    # Provide a draw function that presents the data content.
    # If not provided, the data will be presented using versatile_gui_present
    gui_present_impl: Callable[[DataType], None] | None = None

    # Provide a draw function that presents an editable interface for the data, and returns (True, new_value) if changed
    gui_edit_impl: Callable[[DataType], Tuple[bool, DataType]] | None = None

    # (On hold)
    # Optional serialization and deserialization functions for DataType
    # If provided, these functions will be used to serialize and deserialize the data with a custom dict format.
    # If not provided, "value" will be serialized as a dict of its __dict__ attribute,
    # or as a json string (for int, float, str, bool, and None)
    # to_dict_impl: Callable[[DataType], JsonDict] | None = None
    # from_dict_impl: Callable[[JsonDict], DataType] | None = None

    # default value provider: this function will be called to provide a default value if needed
    default_value_provider: Callable[[], DataType] | None = None

    # on_change: if provided, this function will be called when the value changes
    on_change: Callable[[DataType], None] | None = None


class AnyDataWithGui(Generic[DataType]):
    """
    Instantiate this class with your types, and provide draw functions that presents it content.
    See example implementation for a custom type at the bottom of this file.
    """

    # The value of the data
    _value: DataType | Unspecified | Error = UnspecifiedValue

    # Handlers
    handlers: AnyDataGuiHandlers[DataType]

    def __init__(
        self,
        value: DataType | Unspecified,
        handlers: AnyDataGuiHandlers[DataType],
    ) -> None:
        self.handlers = handlers
        self.value = value

    @property
    def value(self) -> DataType | Unspecified | Error:
        return self._value

    @value.setter
    def value(self, new_value: DataType | Unspecified | Error) -> None:
        self._value = new_value
        if self.handlers.on_change is not None and isinstance(new_value, (Unspecified, Error)) is False:
            self.handlers.on_change(new_value)  # type: ignore

    def to_json(self) -> JsonDict:
        if isinstance(self.value, Unspecified):
            return {"type": "Unspecified"}
        elif isinstance(self.value, Error):
            return {"type": "Error"}
        elif isinstance(self.value, (str, int, float, bool)):
            return {"type": "Primitive", "value": self.value}
        elif self.value is None:
            return {"type": "Primitive", "value": None}
        # elif self.handlers.to_dict_impl is not None:
        #     as_dict = self.handlers.to_dict_impl(self.value)
        #     return {"type": "Custom", "value": as_dict}
        elif hasattr(self.value, "__dict__"):
            as_dict = self.value.__dict__
            return {"type": "Dict", "value": as_dict}
        elif isinstance(self.value, list):
            # return {"type": "List", "value": [AnyDataWithGui(x, self.handlers).to_json() for x in self.value]}
            logging.warning("List serialization not implemented yet")
            return {"type": "List"}
        else:
            logging.warning(f"Cannot serialize {self.value}, it has no __dict__ attribute.")
            return {"type": "Error"}

    def fill_from_json(self, json_data: JsonDict) -> None:
        if "type" not in json_data:
            raise ValueError(f"Cannot deserialize {json_data}")
        if json_data["type"] == "Unspecified":
            self.value = UnspecifiedValue
        elif json_data["type"] == "Error":
            self.value = ErrorValue
        elif json_data["type"] == "Primitive":
            self.value = json_data["value"]
        # elif json_data["type"] == "Custom":
        #     assert self.handlers.from_dict_impl is not None
        #     self.value = self.handlers.from_dict_impl(json_data["value"])
        elif json_data["type"] == "Dict":
            if self.value is None:
                if self.handlers.default_value_provider is None:
                    raise ValueError("Cannot deserialize a None value without a default_value_provider")
                self.value = self.handlers.default_value_provider()
            self.value.__dict__.update(json_data["value"])
        elif json_data["type"] == "List":
            logging.warning("List deserialization not implemented yet")
            return
        else:
            raise ValueError(f"Cannot deserialize {json_data}")

    @final
    def call_gui_present(self) -> None:
        if isinstance(self.value, Unspecified):
            imgui.text("Unspecified!")
        elif isinstance(self.value, Error):
            imgui.text("Error!")
        else:
            if self.handlers.gui_present_impl is None:
                from fiatlight.standard_gui_handlers import versatile_gui_present

                versatile_gui_present(self.value)
            else:
                self.handlers.gui_present_impl(self.value)

    @final
    def call_gui_edit(self) -> bool:
        if self.handlers.gui_edit_impl is None:
            self.call_gui_present()
            return False
        if isinstance(self.value, Error):
            imgui.text("Error!")
        if isinstance(self.value, (Unspecified, Error)):
            imgui.text("Unspecified!")
            imgui.same_line()
            default_value_provider = self.handlers.default_value_provider
            if default_value_provider is None:
                return False
            else:
                if imgui.button(IconsFontAwesome6.ICON_PLUS):
                    self.value = default_value_provider()
                    return True
                else:
                    return False
        else:
            changed, new_value = self.handlers.gui_edit_impl(self.value)
            if changed:
                self.value = new_value
            imgui.same_line()
            if imgui.button(IconsFontAwesome6.ICON_TRASH_CAN):
                self.value = UnspecifiedValue
                changed = True
            return changed


class ParamKind(Enum):
    PositionalOnly = 0
    PositionalOrKeyword = 1
    KeywordOnly = 3


@dataclass
class ParamWithGui(Generic[DataType]):
    name: str
    data_with_gui: AnyDataWithGui[DataType]
    param_kind: ParamKind
    default_value: DataType | Unspecified

    def to_json(self) -> JsonDict:
        data_json = self.data_with_gui.to_json()
        data_dict = {"name": self.name, "data": data_json}
        return data_dict

    def fill_from_json(self, json_data: JsonDict) -> None:
        self.name = json_data["name"]
        if "data" in json_data:
            self.data_with_gui.fill_from_json(json_data["data"])

    def get_value_or_default(self) -> DataType | Unspecified | Error:
        param_value = self.data_with_gui.value
        if isinstance(param_value, Error):
            return ErrorValue
        elif isinstance(param_value, Unspecified):
            return self.default_value
        else:
            return self.data_with_gui.value


@dataclass
class OutputWithGui(Generic[DataType]):
    data_with_gui: AnyDataWithGui[DataType]


##############################################################################################################
# Example implementation for a custom type
##############################################################################################################
class Foo:
    x: int

    def __init__(self, x: int) -> None:
        self.x = x


class FooGuiParams:
    """Any params that could be used to provide additional parameters to the GUI implementation of Foo"""

    pass


def make_foo_gui_handlers(_gui_params: FooGuiParams | None = None) -> AnyDataGuiHandlers[Foo]:
    """_gui_params is not used in this example,
    but could be used to provide additional parameters to the GUI implementation"""
    from imgui_bundle import imgui

    # Edit and present functions
    def edit(value: Foo) -> Tuple[bool, Foo]:
        changed, value.x = imgui.input_int("x", value.x)
        return changed, value

    def present(value: Foo) -> None:
        imgui.text(f"x: {value.x}")

    r = AnyDataGuiHandlers[Foo]()

    r.gui_edit_impl = edit
    r.gui_present_impl = present

    # default value provider
    r.default_value_provider = lambda: Foo(x=0)

    # Optional implementation of serialization and deserialization functions
    # (if not provided, the default serialization will be used, by serializing the __dict__ attribute of the value)
    # r.to_dict_impl = lambda x: {"x": x.x}
    # r.from_dict_impl = lambda d: Foo(x=d["x"])

    return r


def test_foo_with_gui() -> None:
    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.to_gui import ALL_GUI_HANDLERS_FACTORIES

    ALL_GUI_HANDLERS_FACTORIES["Foo"] = make_foo_gui_handlers

    # Use the Foo type with its GUI implementation
    from fiatlight.to_gui import any_value_to_data_with_gui

    foo = Foo(1)
    foo_gui = any_value_to_data_with_gui(foo)
    assert foo_gui.value == foo


if __name__ == "__main__":
    test_foo_with_gui()
