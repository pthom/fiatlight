from fiatlight.fiat_types import DataType, Unspecified, Error, JsonDict, Invalid
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_ctx
from typing import Union
from types import NoneType


class OptionalWithGui(AnyDataWithGui[DataType | None]):
    """Transform a GUI for a DataType into a GUI for an Optional[DataType]"""

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

        self.callbacks.on_fiat_attributes_changed = inner_gui.callbacks.on_fiat_attributes_changed

        if self.inner_gui.callbacks.present is not None:
            self.callbacks.present = self.present

        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict

        self.callbacks.on_heartbeat = self._on_heartbeat

    @staticmethod
    def default_provider() -> DataType | None:
        return None

    def present_str(self, value: DataType | None) -> str:
        if value is None:
            return "None"
        else:
            return self.inner_gui.datatype_value_to_str(value)

    def _on_heartbeat(self) -> bool:
        AnyDataWithGui.propagate_label_and_tooltip(self, self.inner_gui)
        if self.value is None:
            return False
        if self.inner_gui.callbacks.on_heartbeat is not None:
            r = self.inner_gui.callbacks.on_heartbeat()
            return r
        return False

    def present(self, value: DataType | None) -> None:
        assert self.inner_gui.callbacks.present is not None
        if value is None:
            imgui.text("Optional: None")
        else:
            if id(self.inner_gui.value) != id(value):
                self.inner_gui.value = value
            self.inner_gui.callbacks.present(value)

    def edit(self, value: DataType | None) -> tuple[bool, DataType | None]:
        assert not isinstance(value, (Unspecified, Error))
        if value is None:
            assert self.inner_gui.can_construct_default_value()
        fn_edit = self.inner_gui.callbacks.edit

        changed = False
        with imgui_ctx.begin_horizontal("##OptionalH"):
            if value is None:
                imgui.text("None")
                if imgui.button("Set"):
                    default_value = self.inner_gui.construct_default_value()
                    value = default_value
                    changed = True
                fiat_osd.set_widget_tooltip("Set Optional value")
            else:
                if fn_edit is not None:
                    with imgui_ctx.begin_vertical("##OptionalV"):  # Some widgets Expect the standard vertical layout.
                        changed_in_edit, value = fn_edit(value)
                    if changed_in_edit:
                        if isinstance(value, (Unspecified, Error)):
                            raise ValueError("Inner GUI value is Unspecified or Error")
                        changed = True
                else:
                    imgui.text("No edit function!")
                if imgui.button("Set None"):
                    value = None
                    changed = True

        return changed, value

    def on_change(self, value: DataType | None) -> None:
        if value is not None:
            self.inner_gui.value = value
            self.callbacks.edit_collapsible = self.inner_gui.callbacks.edit_collapsible
            self.callbacks.present_collapsible = self.inner_gui.callbacks.present_collapsible
        else:
            self.callbacks.edit_collapsible = False
            self.callbacks.present_collapsible = False

    def _save_to_dict(self, value: DataType | None) -> JsonDict:
        if value is None:
            return {"type": "Optional", "value": None}
        else:
            return {"type": "Optional", "value": self.inner_gui.call_save_to_dict(value)}

    def _load_from_dict(self, json_data: JsonDict) -> DataType | None:
        if json_data["type"] == "Optional":
            if json_data["value"] is None:
                return None
            else:
                r = self.inner_gui.call_load_from_dict(json_data["value"])
                assert not isinstance(r, (Unspecified, Error, Invalid))
                return r
        else:
            raise ValueError("Invalid JSON data for OptionalWithGui")
