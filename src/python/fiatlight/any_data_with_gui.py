"""
This module provides a class to wrap any data with a GUI (AnyDataWithGui), and a class to wrap a named data with a GUI.
See example implementation for a custom type at the bottom of this file.
"""
from fiatlight.fiatlight_types import BoolFunction, VoidFunction
from typing import Optional, Any, final, Callable, TypeVar, Generic
from dataclasses import dataclass
import json

# DataType: TypeAlias = Any
DataType = TypeVar("DataType")


class AnyDataWithGui(Generic[DataType]):
    """
    Instantiate this class with your types, and provide draw functions that presents it content
    """

    # The value of the data
    value: DataType | None = None

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

    # default value provider: if value is None, this function will be called to provide a default value
    default_value: Callable[[], DataType] | None = None

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

    def fill_from_json(self, json_str: str) -> None:
        if json_str == "null":
            self.value = None
        else:
            as_dict_or_value = json.loads(json_str)
            if isinstance(as_dict_or_value, (str, int, float, bool)):
                self.value = as_dict_or_value  # type: ignore
            else:
                as_dict = as_dict_or_value
                if self._has_custom_serialization():
                    assert self.from_dict is not None
                    self.value = self.from_dict(as_dict)
                else:
                    # Ouch, what if value is None?
                    # We need a way to know the type of the value, or to have a default value
                    if self.value is None:
                        if self.default_value is None:
                            raise ValueError("Cannot deserialize a None value without a default_value")
                        self.value = self.default_value()
                    self.value.__dict__.update(as_dict)

    def __init__(
        self,
        value: DataType | None = None,
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


@dataclass
class NamedDataWithGui(Generic[DataType]):
    name: str
    data_with_gui: AnyDataWithGui[DataType]

    def to_json(self) -> str:
        data_json = self.data_with_gui.to_json()
        named_data_dict = {"name": self.name, "data": json.loads(data_json)}
        return json.dumps(named_data_dict)

    def fill_from_json(self, json_str: str) -> None:
        named_data_dict = json.loads(json_str)
        self.name = named_data_dict["name"]
        data_json = json.dumps(named_data_dict["data"])
        self.data_with_gui.fill_from_json(data_json)


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


def make_foo_with_gui(initial_value: Foo | None, gui_params: FooGuiParams | None = None) -> AnyDataWithGui[Foo]:
    """gui_params is not used in this example,
    but could be used to provide additional parameters to the GUI implementation"""
    from imgui_bundle import imgui

    r = AnyDataWithGui[Foo]()
    r.value = initial_value

    # Edit and present functions
    def edit() -> bool:
        assert r.value is not None
        changed, r.value.x = imgui.input_int("x", r.value.x)
        return changed

    def present() -> None:
        assert r.value is not None
        imgui.text(f"x: {r.value.x}")

    r.gui_edit_impl = edit
    r.gui_present_impl = present

    # default value provider
    r.default_value = lambda: Foo(x=0)

    # Optional implementation of serialization and deserialization functions
    # (if not provided, the default serialization will be used, by serializing the __dict__ attribute of the value)
    r.to_dict = lambda x: {"x": x.x}
    r.from_dict = lambda d: Foo(x=d["x"])

    return r


def test_foo_with_gui() -> None:
    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.all_to_gui import all_type_to_gui_info, TypeToGuiInfo

    all_type_to_gui_info().append(TypeToGuiInfo(Foo, make_foo_with_gui, FooGuiParams()))

    # Use the Foo type with its GUI implementation
    from fiatlight.to_gui import any_value_to_data_with_gui

    foo = Foo(1)
    foo_gui = any_value_to_data_with_gui(foo)
    assert foo_gui.value == foo


if __name__ == "__main__":
    test_foo_with_gui()
