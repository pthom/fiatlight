from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_types import DataType, Unspecified, Error, JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import hello_imgui, imgui, imgui_node_editor as ed  # noqa
from enum import Enum
from typing import Type, List, Union
from types import NoneType


class OptionalWithGui(AnyDataWithGui[DataType | None]):
    inner_gui: AnyDataWithGui[DataType]

    def __init__(self, inner_gui: AnyDataWithGui[DataType]) -> None:
        super().__init__(Union[inner_gui._type, NoneType])  # type: ignore
        self.can_be_none = True
        self.inner_gui = inner_gui
        self.callbacks.present_str = self.present_str
        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = self.default_provider
        self.callbacks.clipboard_copy_possible = inner_gui.callbacks.clipboard_copy_possible

        self.callbacks.present_custom_popup_possible = inner_gui.callbacks.present_custom_popup_possible
        self.callbacks.present_custom_popup_required = inner_gui.callbacks.present_custom_popup_required
        self.callbacks.edit_popup_possible = inner_gui.callbacks.edit_popup_possible
        self.callbacks.edit_popup_required = inner_gui.callbacks.edit_popup_required

        if self.inner_gui.callbacks.present_custom is not None:
            self.callbacks.present_custom = self.present_custom

        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict

        self.callbacks.on_heartbeat = self._on_heartbeat

    def default_provider(self) -> DataType | None:
        if self.inner_gui.callbacks.default_value_provider is None:
            return None
        else:
            return self.inner_gui.callbacks.default_value_provider()

    def present_str(self, value: DataType | None) -> str:
        if value is None:
            return "None"
        else:
            inner_present_str = self.inner_gui.callbacks.present_str
            if inner_present_str is not None:
                return inner_present_str(value)
            else:
                return str(value)

    def _on_heartbeat(self) -> bool:
        if self.value is None:
            return False
        if self.inner_gui.callbacks.on_heartbeat is not None:
            r = self.inner_gui.callbacks.on_heartbeat()
            return r
        return False

    def present_custom(self, value: DataType | None) -> None:
        assert self.inner_gui.callbacks.present_custom is not None
        if value is None:
            imgui.text("Optional: None")
        else:
            self.inner_gui.value = value
            self.inner_gui.callbacks.present_custom(value)

    def edit(self, value: DataType | None) -> tuple[bool, DataType | None]:
        assert not isinstance(value, (Unspecified, Error))

        changed = False

        if value is None:
            imgui.begin_horizontal("##OptionalH")
            imgui.text("Optional: None")
            if imgui.button("Set"):
                default_value_provider = self.inner_gui.callbacks.default_value_provider
                assert default_value_provider is not None
                value = default_value_provider()
                changed = True
            fiat_osd.set_widget_tooltip("Set Optional to default value for this type.")
            imgui.end_horizontal()
        else:
            imgui.begin_vertical("##OptionalV")
            imgui.begin_horizontal("##OptionalH")
            imgui.text("Optional: Set")
            if imgui.button("Unset"):
                value = None
                changed = True
            fiat_osd.set_widget_tooltip("Unset Optional.")
            imgui.end_horizontal()
            fn_edit = self.inner_gui.callbacks.edit
            if value is not None and fn_edit is not None:
                changed_in_edit, value = fn_edit(value)
                if changed_in_edit:
                    if isinstance(value, (Unspecified, Error)):
                        raise ValueError("Inner GUI value is Unspecified or Error")
                    changed = True
            else:
                imgui.text("No edit function!")
            imgui.end_vertical()

        return changed, value

    def on_change(self, value: DataType | None) -> None:
        if value is not None:
            self.inner_gui.value = value

    def _save_to_dict(self, value: DataType | None) -> JsonDict:
        if value is None:
            return {"type": "Optional", "value": None}
        else:
            return {"type": "Optional", "value": self.inner_gui.save_to_dict(value)}

    def _load_from_dict(self, json_data: JsonDict) -> DataType | None:
        if json_data["type"] == "Optional":
            if json_data["value"] is None:
                return None
            else:
                r = self.inner_gui.load_from_dict(json_data["value"])
                assert not isinstance(r, (Unspecified, Error))
                return r
        else:
            raise ValueError("Invalid JSON data for OptionalWithGui")


class ListWithGui(AnyDataWithGui[List[DataType]]):
    inner_gui: AnyDataWithGui[DataType]

    popup_max_elements: int = 300
    show_idx: bool = True

    def __init__(self, inner_gui: AnyDataWithGui[DataType]) -> None:
        super().__init__(List[inner_gui._type])  # type: ignore
        self.inner_gui = inner_gui
        self.callbacks.present_str = self.present_str
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: []
        self.callbacks.present_custom = self.present_custom
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str
        self.callbacks.clipboard_copy_possible = inner_gui.callbacks.clipboard_copy_possible
        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict
        self.callbacks.on_heartbeat = self.inner_gui.callbacks.on_heartbeat

    @staticmethod
    def clipboard_copy_str(v: List[DataType]) -> str:
        return str(v)

    def _elements_str(self, value: List[DataType], max_presented_elements: int) -> str:
        nb_elements = len(value)
        nb_digits = len(str(nb_elements))
        strings = []
        for i, element in enumerate(value):
            value_str = self.inner_gui.datatype_value_to_str(element)
            idx_str = str(i).rjust(nb_digits, "0")
            if i >= max_presented_elements:
                strings.append(f"...{nb_elements - max_presented_elements} more elements")
                break
            if self.show_idx:
                strings.append(f"{idx_str}: {value_str}")
            else:
                strings.append(value_str)
        return "\n".join(strings)

    def present_str(self, value: List[DataType]) -> str:
        nb_elements = len(value)
        if nb_elements == 0:
            return "Empty list"
        r = f"List of {nb_elements} elements\n" + self._elements_str(
            value, get_fiat_config().style.list_maximum_elements_in_node
        )
        return r

    def edit(self, value: List[DataType]) -> tuple[bool, List[DataType]]:  # noqa
        raise NotImplementedError("Edit function not implemented for ListWithGui")

    def popup_details(self, value: List[DataType]) -> None:
        imgui.text("List elements")
        _, self.show_idx = imgui.checkbox("Show index", self.show_idx)
        txt = self._elements_str(value, self.popup_max_elements)
        imgui.input_text_multiline("##ListElements", txt, hello_imgui.em_to_vec2(0, 20))

        if self.popup_max_elements < len(value):
            if imgui.button("Show more"):
                self.popup_max_elements += 300

    def present_custom(self, value: List[DataType]) -> None:
        max_elements = get_fiat_config().style.list_maximum_elements_in_node

        def popup_details_value() -> None:
            self.popup_details(value)

        fiat_osd.show_void_detached_window_button(
            "Details",
            "List details",
            popup_details_value,
        )

        txt = self._elements_str(value, max_elements)
        imgui.text(txt)

    def _save_to_dict(self, value: List[DataType]) -> JsonDict:
        r = {"type": "List", "value": [self.inner_gui.save_to_dict(v) for v in value]}
        return r

    def _load_from_dict(self, json_data: JsonDict) -> List[DataType]:
        if json_data["type"] == "List":
            r = [self.inner_gui.load_from_dict(v) for v in json_data["value"]]
            assert not any(isinstance(v, (Unspecified, Error)) for v in r)
            return r  # type: ignore
        else:
            raise ValueError("Invalid JSON data for ListWithGui")


class EnumWithGui(AnyDataWithGui[Enum]):
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

    def edit(self, value: Enum) -> tuple[bool, Enum]:
        assert not isinstance(value, (Unspecified, Error))
        changed = False

        nb_values = len(list(self.enum_type))
        shall_show_two_columns = nb_values >= 3
        if shall_show_two_columns:
            end_first_column = nb_values // 2
        else:
            end_first_column = -1

        for i, enum_value in enumerate(list(self.enum_type)):
            if i == 0:
                imgui.begin_group()
            if imgui.radio_button(enum_value.name, value == enum_value):
                value = enum_value
                changed = True
            if i == end_first_column:
                imgui.end_group()
                imgui.same_line()
                imgui.begin_group()
        imgui.end_group()
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
