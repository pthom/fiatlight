"""
This module provides a class to wrap any data with a GUI (AnyDataWithGui), and a class to wrap a named data with a GUI.
See example implementation for a custom type at the bottom of this file.
"""
from fiatlight.core import Error, ErrorValue, Unspecified, UnspecifiedValue, JsonDict, DataType
from fiatlight.core.any_data_gui_handlers import AnyDataGuiHandlers
from typing import final, Generic, Tuple, Callable
from imgui_bundle import imgui
import logging


class AnyDataWithGui(Generic[DataType]):
    """
    Instantiate this class with your types, and provide draw functions that presents it content.
    See example implementation for a custom type at the bottom of this file.
    """

    # The value of the data
    _value: DataType | Unspecified | Error = UnspecifiedValue

    # Handlers
    handlers: AnyDataGuiHandlers[DataType]

    def __init__(self) -> None:
        self.handlers = AnyDataGuiHandlers.no_handlers()

    @staticmethod
    def from_handlers(handlers: AnyDataGuiHandlers[DataType]) -> "AnyDataWithGui[DataType]":
        r: AnyDataWithGui[DataType] = AnyDataWithGui()
        r.handlers = handlers
        return r

    @staticmethod
    def make_default() -> "AnyDataWithGui[DataType]":
        return AnyDataWithGui()

    @staticmethod
    def from_callbacks(
        present: Callable[[DataType], None] | None = None,
        edit: Callable[[DataType], Tuple[bool, DataType]] | None = None,
        default_value_provider: Callable[[], DataType] | None = None,
        on_change: Callable[[DataType], None] | None = None,
    ) -> "AnyDataWithGui[DataType]":
        r = AnyDataWithGui[DataType]()
        r.handlers.present = present
        r.handlers.edit = edit
        r.handlers.default_value_provider = default_value_provider
        r.handlers.on_change = on_change
        return r

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
            if self.handlers.present is None:
                from fiatlight.core.primitives_gui import versatile_gui_present

                versatile_gui_present(self.value)
            else:
                self.handlers.present(self.value)

    @final
    def call_gui_edit(self) -> bool:
        from fiatlight.widgets import IconsFontAwesome6

        if self.handlers.edit is None:
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
            changed, new_value = self.handlers.edit(self.value)
            if changed:
                self.value = new_value
            imgui.same_line()
            if imgui.button(IconsFontAwesome6.ICON_TRASH_CAN):
                self.value = UnspecifiedValue
                changed = True
            return changed


##############################################################################################################
# Example implementation for a custom type
##############################################################################################################
class Foo:
    x: int

    def __init__(self, x: int) -> None:
        self.x = x


class FooWithGui(AnyDataWithGui[Foo]):
    def __init__(self) -> None:
        # Edit and present functions
        def edit(value: Foo) -> Tuple[bool, Foo]:
            changed, value.x = imgui.input_int("x", value.x)
            return changed, value

        def present(value: Foo) -> None:
            imgui.text(f"x: {value.x}")

        # Optional implementation of serialization and deserialization functions
        # (if not provided, the default serialization will be used, by serializing the __dict__ attribute of the value)
        # r.to_dict_impl = lambda x: {"x": x.x}
        # r.from_dict_impl = lambda d: Foo(x=d["x"])

        super().__init__()
        self.handlers.edit = edit
        self.handlers.present = present
        self.handlers.default_value_provider = lambda: Foo(x=0)


def test_foo_with_gui() -> None:
    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.core.to_gui import ALL_GUI_FACTORIES, any_value_to_data_with_gui

    ALL_GUI_FACTORIES["Foo"] = FooWithGui

    foo = Foo(1)
    foo_gui = any_value_to_data_with_gui(foo)
    assert foo_gui.value == foo


if __name__ == "__main__":
    test_foo_with_gui()
