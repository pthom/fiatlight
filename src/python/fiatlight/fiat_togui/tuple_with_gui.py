"""TupleWithGui: adds a GUI to a tuple of elements, each with its own GUI"""

from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_core.any_data_with_gui import GuiHeaderLineParams
from fiatlight.fiat_types import Unspecified, Error, JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_types import FiatAttributes
from imgui_bundle import imgui_ctx, ImVec4
from typing import Any, Tuple, cast


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
        tuple_type = cast(Tuple[tuple(types)], tuple)  # type: ignore
        super().__init__(tuple_type)
        self._inner_guis = inner_guis

        # We set the _can_set_unspecified_or_default to False for all parameters
        for i, inner_gui in enumerate(inner_guis):
            inner_gui.label = f"{i} ({inner_gui.datatype_basename()})"
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
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

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
            default_values.append(inner_gui.value)
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

    def sub_items_collapse_or_expand(self, collapse_or_expand: AnyDataWithGui.CollapseOrExpandChildren) -> None:
        from fiatlight.fiat_togui.dataclass_like_gui import DataclassLikeGui

        new_expanded_state = collapse_or_expand == AnyDataWithGui.CollapseOrExpandChildren.expand

        for inner_gui in self._inner_guis:
            if inner_gui.callbacks.present_collapsible:
                inner_gui._expanded = new_expanded_state
                if isinstance(inner_gui, (DataclassLikeGui, TupleWithGui)):
                    inner_gui.sub_items_collapse_or_expand(collapse_or_expand)

    def sub_items_will_collapse_or_expand(
        self, present_or_edit: AnyDataWithGui.PresentOrEdit
    ) -> AnyDataWithGui.CollapseOrExpandChildren:
        for inner_gui in self._inner_guis:
            if (
                inner_gui.callbacks.present_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.present
                and inner_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpandChildren.collapse
            if (
                inner_gui.callbacks.edit_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.edit
                and inner_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpandChildren.collapse
        return AnyDataWithGui.CollapseOrExpandChildren.expand

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
            fiat_attributes_this_element = FiatAttributes({})
            for item, value in fiat_attributes.items():
                if item.startswith(prefix):
                    fiat_attributes_this_element[item[len(prefix) :]] = value
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
                        GuiHeaderLineParams(show_clipboard_button=False, parent_name=self.datatype_basename())
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
                parent_name = self.datatype_basename()
                changed_in_edit = inner_gui.gui_edit_customizable(
                    GuiHeaderLineParams(show_clipboard_button=False, parent_name=parent_name)
                )
                new_values.append(inner_gui.value)
                if changed_in_edit:
                    changed = True

        if changed:
            r = tuple(new_values)
            return changed, r
        else:
            return False, value

    @staticmethod
    def _member_label_color() -> ImVec4:
        from fiatlight.fiat_config import FiatColorType

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

    def save_gui_options_to_json(self) -> JsonDict:
        # We only save the GUI options, not the data!
        options = []
        for inner_gui in self._inner_guis:
            options.append(inner_gui.call_save_gui_options_to_json())
        return {"type": "Tuple", "options": options}

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        # We only load the GUI options, not the data!
        if json["type"] != "Tuple":
            raise ValueError("Invalid JSON data for TupleWithGui")
        if len(json["options"]) != len(self._inner_guis):
            raise ValueError("The length of the provided tuple does not match the number of inner GUIs.")
        for i in range(len(json["options"])):
            inner_gui = self._inner_guis[i]
            inner_gui.call_load_gui_options_from_json(json["options"][i])
