from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_types import DataType, Unspecified, Error, JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from imgui_bundle import hello_imgui, imgui
from typing import List


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
        self.callbacks.present = self.present
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str
        self.callbacks.clipboard_copy_possible = inner_gui.callbacks.clipboard_copy_possible
        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict
        self.callbacks.on_heartbeat = self.inner_gui.callbacks.on_heartbeat
        self.callbacks.on_fiat_attributes_changed = self.inner_gui.callbacks.on_fiat_attributes_changed

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

    def present(self, value: List[DataType]) -> None:
        max_elements = get_fiat_config().style.list_maximum_elements_in_node
        txt = self._elements_str(value, max_elements)
        imgui.text(txt)

        if imgui.button("Details"):
            imgui.open_popup("DetailsPopup")
        popup_visible, _ = imgui.begin_popup_modal("DetailsPopup")
        if popup_visible:
            self.popup_details(value)
            if imgui.button("Close"):
                imgui.close_current_popup()
            imgui.end_popup()

    def _save_to_dict(self, value: List[DataType]) -> JsonDict:
        r = {"type": "List", "value": [self.inner_gui.call_save_to_dict(v) for v in value]}
        return r

    def _load_from_dict(self, json_data: JsonDict) -> List[DataType]:
        if json_data["type"] == "List":
            r = [self.inner_gui.call_load_from_dict(v) for v in json_data["value"]]
            assert not any(isinstance(v, (Unspecified, Error)) for v in r)
            return r  # type: ignore
        else:
            raise ValueError("Invalid JSON data for ListWithGui")
