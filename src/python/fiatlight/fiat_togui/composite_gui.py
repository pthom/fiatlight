from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_core.any_data_with_gui import GuiHeaderLineParams
from fiatlight.fiat_types import DataType, Unspecified, Error, JsonDict, InvalidValue
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd
from fiatlight.fiat_types import FiatAttributes
from imgui_bundle import hello_imgui, imgui, imgui_ctx, ImVec4
from enum import Enum
from typing import Type, List, Union, Any
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

        self.callbacks.present_node_compatible = inner_gui.callbacks.present_node_compatible
        self.callbacks.edit_node_compatible = inner_gui.callbacks.edit_node_compatible
        self.callbacks.on_fiat_attributes_changed = inner_gui.callbacks.on_fiat_attributes_changed

        if self.inner_gui.callbacks.present is not None:
            self.callbacks.present = self.present

        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict

        self.callbacks.on_heartbeat = self._on_heartbeat

    def default_provider(self) -> DataType | None:
        if not self.inner_gui.can_construct_default_value():
            return None
        else:
            return self.inner_gui.construct_default_value()

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

        changed = False

        if value is None:
            imgui.begin_horizontal("##OptionalH")
            imgui.text("Optional: None")
            if imgui.button("Set"):
                assert self.inner_gui.can_construct_default_value()
                value = self.inner_gui.construct_default_value()
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
                assert not isinstance(r, (Unspecified, Error, InvalidValue))
                return r
        else:
            raise ValueError("Invalid JSON data for OptionalWithGui")


class TupleWithGui(AnyDataWithGui[tuple[Any, ...]]):
    """A GUI for a tuple of elements, each with its own GUI"""

    # The implementation for this resembles DataclassLikeGui
    _inner_guis: tuple[AnyDataWithGui[Any], ...]

    class _Init_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Factor
        # ------------------------------------------------------------------------------------------------------------------
        """

    def __init__(self, inner_guis: tuple[AnyDataWithGui[Any], ...], fiat_attributes: FiatAttributes) -> None:
        # Constructing a tuple type for all _inner_guis
        types = tuple(inner_gui._type for inner_gui in inner_guis)
        super().__init__(types)  # type: ignore
        self._inner_guis = inner_guis

        # We set the _can_set_unspecified_or_default to False for all parameters
        for i, inner_gui in enumerate(inner_guis):
            inner_gui.label = f"{i} ({inner_gui.datatype_name()})"
            inner_gui._can_set_unspecified_or_default = False
            inner_gui.label_color = self._member_label_color()

        self.fill_callbacks()
        if fiat_attributes is not None:
            self.on_fiat_attributes_changed(fiat_attributes)

    def fill_callbacks(self) -> None:
        self.callbacks.present_str = self.present_str
        self.callbacks.present = self.present
        self.callbacks.edit = self.edit

        # It is always possible to collapse a tuple
        self.callbacks.edit_collapsible = True
        self.callbacks.present_collapsible = True

        self.callbacks.present_node_compatible = all(
            inner_gui.callbacks.present_node_compatible for inner_gui in self._inner_guis
        )
        self.callbacks.edit_node_compatible = all(
            inner_gui.callbacks.edit_node_compatible for inner_gui in self._inner_guis
        )

        self.callbacks.on_change = self.on_change
        self.callbacks.on_exit = self.on_exit
        self.callbacks.on_heartbeat = self._on_heartbeat
        self.callbacks.default_value_provider = self.default_provider
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changed

        self.callbacks.clipboard_copy_possible = all(
            inner_gui.callbacks.clipboard_copy_possible for inner_gui in self._inner_guis
        )
        if self.callbacks.clipboard_copy_possible:
            self.callbacks.clipboard_copy_str = self.clipboard_copy_str

        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.load_from_dict = self._load_from_dict

    class _Factor_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Factor
        # ------------------------------------------------------------------------------------------------------------------
        """

    def default_provider(self) -> tuple[Any, ...]:
        default_values: list[Any] = []
        for i, inner_gui in enumerate(self._inner_guis):
            if not inner_gui.can_construct_default_value():
                raise ValueError(f"Tuple element {i} has no default value provider in class {self._type}")
            inner_gui.value = inner_gui.construct_default_value()
        return tuple(default_values)

    class _Utils_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Utils
        # ------------------------------------------------------------------------------------------------------------------
        """

    def is_fully_specified(self) -> bool:
        has_unspecified = False
        for inner_gui in self._inner_guis:
            param_value = inner_gui.value
            if isinstance(param_value, (Unspecified, Error)):
                has_unspecified = True
                break
        return not has_unspecified

    class _SubItemsCollapse_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            SubItems collapse
        # ------------------------------------------------------------------------------------------------------------------
        """

    def sub_items_can_collapse(self, present_or_edit: AnyDataWithGui.PresentOrEdit) -> bool:
        for inner_gui in self._inner_guis:
            if inner_gui.callbacks.present_collapsible and present_or_edit == AnyDataWithGui.PresentOrEdit.present:
                return True
            if inner_gui.callbacks.edit_collapsible and present_or_edit == AnyDataWithGui.PresentOrEdit.edit:
                return True
        return False

    def sub_items_collapse_or_expand(self, collapse_or_expand: AnyDataWithGui.CollapseOrExpand) -> None:
        from fiatlight.fiat_togui.dataclass_gui import DataclassLikeGui

        new_expanded_state = collapse_or_expand == AnyDataWithGui.CollapseOrExpand.expand

        for inner_gui in self._inner_guis:
            if inner_gui.callbacks.present_collapsible:
                inner_gui._expanded = new_expanded_state
                if isinstance(inner_gui, (DataclassLikeGui, TupleWithGui)):
                    inner_gui.sub_items_collapse_or_expand(collapse_or_expand)

    def sub_items_will_collapse_or_expand(
        self, present_or_edit: AnyDataWithGui.PresentOrEdit
    ) -> AnyDataWithGui.CollapseOrExpand:
        for inner_gui in self._inner_guis:
            if (
                inner_gui.callbacks.present_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.present
                and inner_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpand.collapse
            if (
                inner_gui.callbacks.edit_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.edit
                and inner_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpand.collapse
        return AnyDataWithGui.CollapseOrExpand.expand

    class _Callbacks_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Callbacks
        # ------------------------------------------------------------------------------------------------------------------
        """

    def on_change(self, value: tuple[Any, ...]) -> None:
        if len(value) != len(self._inner_guis):
            raise ValueError("The length of the provided tuple does not match the number of inner GUIs.")
        for i in range(len(value)):
            param_value = value[i]
            self._inner_guis[i].value = param_value  # will fire on_change

    def on_exit(self) -> None:
        for inner_gui in self._inner_guis:
            param_on_exit = inner_gui.callbacks.on_exit
            if param_on_exit is not None:
                param_on_exit()

    def on_fiat_attributes_changed(self, fiat_attributes: FiatAttributes) -> None:
        for i, element_gui in enumerate(self._inner_guis):
            # Each tuple gui element will only receive the attributes that concern it.
            prefix = f"{i}_"
            fiat_attributes_this_element = FiatAttributes(
                {item: value for item, value in fiat_attributes.items() if item.startswith(prefix)}
            )
            element_gui.merge_fiat_attributes(fiat_attributes_this_element)

    def _on_heartbeat(self) -> bool:
        # AnyDataWithGui.propagate_label_and_tooltip(self, self.inner_gui)
        if self.value is None:
            return False
        changed = False
        for inner_gui in self._inner_guis:
            if inner_gui.callbacks.on_heartbeat is not None:
                r = inner_gui.callbacks.on_heartbeat()
                if r:
                    changed = True
        return changed

    def clipboard_copy_str(self, value: tuple[Any, ...]) -> str:
        if len(value) != len(self._inner_guis):
            raise ValueError("The length of the provided tuple does not match the number of inner GUIs.")

        present_strs = []
        for val, inner_gui in zip(value, self._inner_guis):
            present_strs.append(inner_gui.datatype_value_to_clipboard_str(val))

        r = f"({', '.join(present_strs)})"
        return r

    class _Gui_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            GUI
        # ------------------------------------------------------------------------------------------------------------------
        """

    def present_str(self, value: tuple[Any, ...]) -> str:
        if value is None:
            return "None"

        if len(value) != len(self._inner_guis):
            raise ValueError("The length of the provided tuple does not match the number of inner GUIs.")

        present_strs = []
        for val, inner_gui in zip(value, self._inner_guis):
            present_strs.append(inner_gui.datatype_value_to_str(val))

        return f"({', '.join(present_strs)})"

    def present(self, _value: tuple[Any, ...]) -> None:
        # the parameter is not used, because we have the data in self._parameters_with_gui
        with imgui_ctx.begin_vertical("##TupleWithGui_present"):
            for inner_gui in self._inner_guis:
                with imgui_ctx.push_obj_id(inner_gui):
                    inner_gui.gui_present_customizable(
                        GuiHeaderLineParams(show_clipboard_button=False, parent_name=self.datatype_name())
                    )

    def edit(self, value: tuple[Any, ...]) -> tuple[bool, tuple[Any, ...]]:
        changed = False
        if len(value) != len(self._inner_guis):
            raise RuntimeError(
                f"""
                TupleWithGui: The length of the provided tuple {len(value)} does not match
                the number of inner GUIs ({len(self._inner_guis)})."""
            )
        new_values = []
        for i, inner_gui in enumerate(self._inner_guis):
            with imgui_ctx.push_obj_id(inner_gui):
                inner_gui.value = value[i]
                changed_in_edit = inner_gui.gui_edit_customizable(
                    GuiHeaderLineParams(show_clipboard_button=False, parent_name=self.datatype_name())
                )
                if changed_in_edit:
                    new_values.append(inner_gui.value)
                    changed = True

        if changed:
            r = tuple(new_values)
            return changed, r
        else:
            return False, value

    @staticmethod
    def _member_label_color() -> ImVec4:
        from fiatlight.fiat_config import get_fiat_config, FiatColorType

        r = get_fiat_config().style.color_as_vec4(FiatColorType.TupleLabel)
        return r

    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Serialization
        # ------------------------------------------------------------------------------------------------------------------
        """

    def _save_to_dict(self, value: tuple[Any, ...]) -> JsonDict:
        values_dicts = []
        if len(value) != len(self._inner_guis):
            raise ValueError("The length of the provided tuple does not match the number of inner GUIs.")
        for i in range(len(value)):
            inner_gui = self._inner_guis[i]
            values_dicts.append(inner_gui.call_save_to_dict(value[i]))
        r = {"type": "Tuple", "values": values_dicts}
        return r

    def _load_from_dict(self, json_data: JsonDict) -> tuple[Any, ...]:
        if json_data["type"] != "Tuple":
            raise ValueError("Invalid JSON data for TupleWithGui")
        if len(json_data["values"]) != len(self._inner_guis):
            raise ValueError("The length of the provided tuple does not match the number of inner GUIs.")
        values = []
        for i in range(len(json_data["values"])):
            inner_gui = self._inner_guis[i]
            values.append(inner_gui.call_load_from_dict(json_data["values"][i]))
        r = tuple(values)
        return r


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

        def popup_details_value() -> None:
            self.popup_details(value)

        detached_window_params = fiat_osd.DetachedWindowParams(
            unique_id="ListWithGuiPopup" + str(id(self)),
            window_name=f"{self.label}  - list of {len(value)} elements",
            button_label="List content",
            gui_function=popup_details_value,
        )
        fiat_osd.show_void_detached_window_button(detached_window_params)

        txt = self._elements_str(value, max_elements)
        imgui.text(txt)

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


class EnumWithGui(AnyDataWithGui[Enum]):
    """An automatic GUI for any Enum. Will show radio buttons for each enum value, on two columns"""

    enum_type: Type[Enum]

    _can_edit_one_line: bool = False

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

        self._check_can_edit_one_line()

    def _check_can_edit_one_line(self) -> None:
        total_len = 0
        for enum_value in list(self.enum_type):
            total_len += len(enum_value.name) + 3
        if total_len < 50:
            self._can_edit_one_line = True
            self.callbacks.edit_collapsible = False

    def edit(self, value: Enum) -> tuple[bool, Enum]:
        assert not isinstance(value, (Unspecified, Error))
        changed = False
        nb_values = len(list(self.enum_type))

        if self._can_edit_one_line:
            for i, enum_value in enumerate(list(self.enum_type)):
                if i > 0:
                    imgui.same_line()
                if imgui.radio_button(enum_value.name, value == enum_value):
                    value = enum_value
                    changed = True
        else:
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
