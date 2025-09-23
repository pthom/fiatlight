from fiatlight.fiat_types import Unspecified, Error, JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from imgui_bundle import imgui, hello_imgui
from enum import Enum
from typing import Type


class EnumWithGui(AnyDataWithGui[Enum]):
    """An automatic GUI for any Enum. Will show radio buttons for each enum value, on two columns"""

    enum_type: Type[Enum]

    def __init__(self, enum_type: Type[Enum]) -> None:
        super().__init__(enum_type)
        self.enum_type = enum_type

        nb_values = len(list(self.enum_type))
        assert nb_values > 0

        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: list(self.enum_type)[0]
        self.callbacks.clipboard_copy_possible = True

        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict
        self.callbacks.on_heartbeat = None
        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    def _enum_value_label(self, enum_value: Enum) -> str:
        if hasattr(self.enum_type, "use_value_as_label"):
            if self.enum_type.use_value_as_label:
                return str(enum_value.value)

        custom_label_attr_name = enum_value.name + "__label"
        if hasattr(self.enum_type, custom_label_attr_name):
            return str(getattr(self.enum_type, custom_label_attr_name))
        return enum_value.name

    def _enum_value_tooltip(self, enum_value: Enum) -> str:
        custom_tooltip_attr_name = enum_value.name + "__tooltip"
        if hasattr(self.enum_type, custom_tooltip_attr_name):
            return str(getattr(self.enum_type, custom_tooltip_attr_name))
        return ""

    def edit(self, value: Enum) -> tuple[bool, Enum]:
        assert not isinstance(value, (Unspecified, Error))
        changed = False
        imgui.push_id(str(id(self)))

        imgui.set_next_item_width(hello_imgui.em_size(10))
        if imgui.begin_combo(label="##", preview_value=self._enum_value_label(value)):
            for i, enum_value in enumerate(list(self.enum_type)):
                label = self._enum_value_label(enum_value)
                tooltip = self._enum_value_tooltip(enum_value)
                is_selected = enum_value == value
                clicked = imgui.radio_button(label, is_selected)
                if len(tooltip) > 0:
                    imgui.set_item_tooltip(tooltip)
                if clicked:
                    value = enum_value
                    changed = True
                    imgui.close_current_popup()
            imgui.end_combo()

        imgui.pop_id()
        return changed, value

    def create_from_name(self, name: str) -> Enum:
        return self.enum_type[name]

    def _save_to_dict(self, value: Enum) -> JsonDict:
        r = {"type": "Enum", "value_name": value.name, "class": value.__class__.__name__}
        return r

    def _load_from_dict(self, json_data: JsonDict) -> Enum:
        if json_data["type"] == "Enum":
            if "value_name" not in json_data:
                raise ValueError("Invalid JSON data for EnumWithGui")
            if "class" not in json_data:
                raise ValueError("Invalid JSON data for EnumWithGui")
            class_name = json_data["class"]
            if class_name != self.enum_type.__name__:
                raise ValueError("Invalid JSON data for EnumWithGui")

            value_name = json_data["value_name"]
            r = self.create_from_name(value_name)
            return r
        else:
            raise ValueError("Invalid JSON data for EnumWithGui")
