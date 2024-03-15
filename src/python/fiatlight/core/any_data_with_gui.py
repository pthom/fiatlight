"""
This module provides a class to wrap any data with a GUI (AnyDataWithGui), and a class to wrap a named data with a GUI.
See example implementation for a custom type at the bottom of this file.
"""
from fiatlight.core import (
    Error,
    ErrorValue,
    Unspecified,
    UnspecifiedValue,
    JsonDict,
    DataType,
    VoidFunction,
    BoolFunction,
)
from fiatlight.core.any_data_gui_callbacks import AnyDataGuiCallbacks
from fiatlight.widgets.fontawesome6_ctx import fontawesome_6_ctx, icons_fontawesome_6
from typing import final, Generic, Callable
from imgui_bundle import imgui, icons_fontawesome_4
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
    def make_default() -> "AnyDataWithGui[DataType]":
        return AnyDataWithGui()

    @staticmethod
    def from_callbacks(
        present: VoidFunction | None = None,
        edit: BoolFunction | None = None,
        default_value_provider: Callable[[], DataType] | None = None,
        on_change: VoidFunction | None = None,
    ) -> "AnyDataWithGui[DataType]":
        r = AnyDataWithGui[DataType]()
        r.callbacks.present = present
        r.callbacks.edit = edit
        r.callbacks.default_value_provider = default_value_provider
        r.callbacks.on_change = on_change
        return r

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

    def to_json(self) -> JsonDict:
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
        #     assert self.callbacks.from_dict_impl is not None
        #     self.value = self.callbacks.from_dict_impl(json_data["value"])
        elif json_data["type"] == "Dict":
            if self.value is UnspecifiedValue:
                if self.callbacks.default_value_provider is None:
                    raise ValueError("Cannot deserialize a None value without a default_value_provider")
                self.value = self.callbacks.default_value_provider()
            self.value.__dict__.update(json_data["value"])
        elif json_data["type"] == "List":
            logging.warning("List deserialization not implemented yet")
            return
        else:
            raise ValueError(f"Cannot deserialize {json_data}")

    @final
    def call_gui_present(self, default_param_value: Unspecified | DataType = UnspecifiedValue) -> None:
        from fiatlight import widgets

        if isinstance(self.value, Unspecified):
            if default_param_value is UnspecifiedValue:
                # imgui.text("Unspecified!")
                with fontawesome_6_ctx():
                    imgui.text(icons_fontawesome_6.ICON_FA_CROSS)
            else:
                try:
                    default_str = str(default_param_value)
                except Exception:
                    default_str = "???"
                imgui.begin_group()
                # imgui.text("Unspecified!")
                with fontawesome_6_ctx():
                    imgui.text(icons_fontawesome_6.ICON_FA_CROSS)
                widgets.text_maybe_truncated("Default: " + default_str, max_width_chars=40, max_lines=3)
                imgui.end_group()

        elif isinstance(self.value, Error):
            imgui.text("Error!")
        else:
            if self.callbacks.present is None:
                from fiatlight.core.primitives_gui import versatile_gui_present

                versatile_gui_present(self.value)
            else:
                self.callbacks.present()

    @final
    def call_gui_edit(
        self, *, display_trash: bool = True, default_param_value: Unspecified | DataType = UnspecifiedValue
    ) -> bool:
        # (display_trash is set to False for OptionalWithGui's inner_gui)
        from fiatlight import widgets

        if self.callbacks.edit is None:
            self.call_gui_present()
            return False
        if isinstance(self.value, Error):
            imgui.text("Error!")
        if isinstance(self.value, (Unspecified, Error)):
            if default_param_value is not UnspecifiedValue:
                try:
                    default_str = str(default_param_value)
                except Exception:
                    default_str = "???"
                imgui.begin_group()
                imgui.text("Unspecified!")
                widgets.text_maybe_truncated("Default: " + default_str, max_width_chars=40, max_lines=3)
                imgui.end_group()

                imgui.same_line()
                if imgui.button(icons_fontawesome_4.ICON_FA_PLUS):
                    self.value = default_param_value
                    return True
                else:
                    return False
            else:
                imgui.text("Unspecified!")
                imgui.same_line()
                default_value_provider = self.callbacks.default_value_provider
                if default_value_provider is None:
                    return False
                else:
                    if imgui.button(icons_fontawesome_4.ICON_FA_PLUS):
                        self.value = default_value_provider()
                        return True
                    else:
                        return False
        else:
            changed = self.callbacks.edit()
            imgui.same_line()
            if display_trash:
                if imgui.button(icons_fontawesome_4.ICON_FA_TRASH):
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
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.present = self.present
        self.callbacks.default_value_provider = lambda: Foo(x=0)

    # Edit and present functions
    def edit(self) -> bool:
        assert isinstance(self.value, Foo)
        changed, self.value.x = imgui.input_int("x", self.value.x)
        return changed

    def present(self) -> None:
        imgui.text(f"x: {self.get_actual_value()}")


def test_foo_with_gui() -> None:
    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.core.to_gui import ALL_GUI_FACTORIES, any_value_to_data_with_gui

    ALL_GUI_FACTORIES["Foo"] = FooWithGui

    foo = Foo(1)
    foo_gui = any_value_to_data_with_gui(foo)
    assert foo_gui.value == foo


if __name__ == "__main__":
    test_foo_with_gui()
