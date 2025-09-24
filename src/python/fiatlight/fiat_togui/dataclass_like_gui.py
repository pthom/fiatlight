from fiatlight.fiat_core import AnyDataWithGui, FunctionWithGui, ParamWithGui
from fiatlight.fiat_core.any_data_with_gui import GuiHeaderLineParams
from fiatlight.fiat_types import JsonDict, Unspecified, Error, Invalid
from fiatlight.fiat_types.base_types import FiatAttributes
from fiatlight.fiat_config import get_fiat_config, FiatColorType
from imgui_bundle import imgui_ctx
from typing import Type, Any, TypeVar, List

# A type variable that represents a dataclass type, or a pydantic BaseModel type
DataclassLikeType = TypeVar("DataclassLikeType")


class DataclassLikeGui(AnyDataWithGui[DataclassLikeType]):
    """Base GUI class for a dataclass or a pydantic model"""

    # The implementation for this resembles TupleWithGui

    _parameters_with_gui: List[ParamWithGui[Any]]

    class _Initialization_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Initialization
        # ------------------------------------------------------------------------------------------------------------------
        """

    def __init__(self, dataclass_type: Type[DataclassLikeType], fiat_attributes: FiatAttributes | None = None) -> None:
        super().__init__(dataclass_type)

        # In order to find the members of the dataclass, we
        # create a FunctionWithGui instance with the dataclass type
        # so that FunctionWithGui can find the members of the dataclass
        # and associate them with GUI
        constructor_gui = FunctionWithGui(
            dataclass_type, fiat_attributes=fiat_attributes, is_dataclass_init_method=True
        )
        self._parameters_with_gui = constructor_gui._inputs_with_gui

        # We set the _can_set_unspecified_or_default to False for all parameters
        for parameters_with_gui in self._parameters_with_gui:
            parameters_with_gui.data_with_gui._can_set_unspecified_or_default = False

        self.fill_callbacks()
        if fiat_attributes is not None:
            self.on_fiat_attributes_changed(fiat_attributes)

    def fill_callbacks(self) -> None:
        self.callbacks.present = self.present
        self.callbacks.edit = self.edit

        # It is always possible to collapse a dataclass
        self.callbacks.edit_collapsible = True
        self.callbacks.present_collapsible = True

        self.callbacks.on_change = self.on_change
        self.callbacks.on_exit = self.on_exit
        self.callbacks.on_heartbeat = self.on_heartbeat
        self.callbacks.default_value_provider = self.default_value_provider
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changed

        self.callbacks.clipboard_copy_possible = all(
            param_gui.data_with_gui.callbacks.clipboard_copy_possible for param_gui in self._parameters_with_gui
        )
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str

        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

    class _Factor_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Factor
        # ------------------------------------------------------------------------------------------------------------------
        """

    def factor_invalid_instance_with_edited_values(self) -> Invalid[DataclassLikeType]:
        edited_param_values = self._get_edited_param_values()

        invalid_instance: DataclassLikeType
        if self.can_construct_default_value():
            try:
                invalid_instance = self.construct_default_value()
                for param_name, param_value in edited_param_values.items():
                    # param_value is either Invalid or a valid value: invalid_instance is indeed invalid!
                    invalid_instance.__setattr__(param_name, param_value)
                invalid_result = Invalid(invalid_value=invalid_instance, error_message="Invalid values")
                return invalid_result
            except Exception:
                raise TypeError(
                    f"""
                    factor_invalid_instance_with_edited_values() for class {self.datatype_qualified_name()}
                    construct_default_value() raised an exception, so cannot transmit invalid values
                """
                )
        else:
            raise TypeError(
                f"""
                factor_invalid_instance_with_edited_values() for class {self.datatype_qualified_name()}
                Cannot construct a default value for the dataclass, so cannot transmit invalid values
            """
            )

    def factor_dataclass_instance_with_edited_values(self) -> DataclassLikeType | Invalid[DataclassLikeType]:
        assert self._type is not None

        param_values = self._get_edited_param_values()
        if any(isinstance(param_value, (Error, Unspecified)) for param_value in param_values.values()):
            raise ValueError("Cannot construct a dataclass instance with an Error or Unspecified value")

        if not any(isinstance(param_value, Invalid) for param_value in param_values.values()):
            instance = self._type(**param_values)
            return instance
        else:
            # Handle invalid values
            return self.factor_invalid_instance_with_edited_values()

    def default_value_provider(self) -> DataclassLikeType:
        assert self._type is not None

        default_param_values = {}
        for param_gui in self._parameters_with_gui:
            param_name = param_gui.name
            if not isinstance(param_gui.default_value, Unspecified):
                default_param_values[param_name] = param_gui.default_value
            else:
                if not param_gui.data_with_gui.can_construct_default_value():
                    raise ValueError(f"Parameter {param_gui.name} has no default value provider in class {self._type}")
                default_param_values[param_name] = param_gui.data_with_gui.construct_default_value()

        current_param_values = self._get_edited_param_values()
        self._set_edited_param_values(default_param_values)
        try:
            default_value = self.factor_dataclass_instance_with_edited_values()
        except ValueError as e:
            raise ValueError(
                f"""
                DataclassLikeGui({self.datatype_qualified_name()}).default_value_provider()
                raised an exception!
                It probably returns a default value that does not pass validation! Please check your default values.
                {e}
            """
            ) from e
        self._set_edited_param_values(current_param_values)

        if isinstance(default_value, (Error, Invalid)):
            raise ValueError(
                f"""
            DataclassLikeGui({self.datatype_qualified_name()}).default_value_provider
            returned a default value that does not pass validation!
            Please check your default values.
            """
            )
        return default_value

    class _Utils_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Utils
        # ------------------------------------------------------------------------------------------------------------------
        """

    def has_param_of_name(self, name: str) -> bool:
        for param_gui in self._parameters_with_gui:
            if param_gui.name == name:
                return True
        return False

    def param_of_name(self, name: str) -> ParamWithGui[Any]:
        for param_gui in self._parameters_with_gui:
            if param_gui.name == name:
                return param_gui
        raise ValueError(f"Parameter {name} not found in class {self._type}")

    def is_fully_specified(self) -> bool:
        has_unspecified = False
        for param_gui in self._parameters_with_gui:
            param_value = param_gui.data_with_gui.value
            if isinstance(param_value, (Unspecified, Error)):
                has_unspecified = True
                break
        return not has_unspecified

    def _get_edited_param_values(self) -> dict[str, Any]:
        param_values = {}
        for param_gui in self._parameters_with_gui:
            param_values[param_gui.name] = param_gui.data_with_gui.value
        return param_values

    def _set_edited_param_values(self, values: dict[str, Any]) -> None:
        for param_gui in self._parameters_with_gui:
            param_gui.data_with_gui.value = values[param_gui.name]

    class _SubItemsCollapse_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            SubItems collapse
        # ------------------------------------------------------------------------------------------------------------------
        """

    def sub_items_can_collapse(self, present_or_edit: AnyDataWithGui.PresentOrEdit) -> bool:
        for param_gui in self._parameters_with_gui:
            if (
                param_gui.data_with_gui.callbacks.present_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.present
            ):
                return True
            if (
                param_gui.data_with_gui.callbacks.edit_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.edit
            ):
                return True
        return False

    def sub_items_collapse_or_expand(self, collapse_or_expand: AnyDataWithGui.CollapseOrExpandChildren) -> None:
        from fiatlight.fiat_togui.tuple_with_gui import TupleWithGui

        new_expanded_state = collapse_or_expand == AnyDataWithGui.CollapseOrExpandChildren.expand

        for param_gui in self._parameters_with_gui:
            if param_gui.data_with_gui.callbacks.present_collapsible:
                param_gui.data_with_gui._expanded = new_expanded_state
                if isinstance(param_gui.data_with_gui, (DataclassLikeGui, TupleWithGui)):
                    param_gui.data_with_gui.sub_items_collapse_or_expand(collapse_or_expand)

    def sub_items_will_collapse_or_expand(
        self, present_or_edit: AnyDataWithGui.PresentOrEdit
    ) -> AnyDataWithGui.CollapseOrExpandChildren:
        for param_gui in self._parameters_with_gui:
            if (
                param_gui.data_with_gui.callbacks.present_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.present
                and param_gui.data_with_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpandChildren.collapse
            if (
                param_gui.data_with_gui.callbacks.edit_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.edit
                and param_gui.data_with_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpandChildren.collapse
        return AnyDataWithGui.CollapseOrExpandChildren.expand

    class _Callbacks_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Callbacks
        # ------------------------------------------------------------------------------------------------------------------
        """

    def on_change(self, value: DataclassLikeType) -> None:
        for param_gui in self._parameters_with_gui:
            if not hasattr(value, param_gui.name):
                raise ValueError(f"Object does not have attribute {param_gui.name}")
            param_value = getattr(value, param_gui.name)
            param_gui.data_with_gui.value = param_value  # will fire on_change

    def on_exit(self) -> None:
        for param_gui in self._parameters_with_gui:
            param_on_exit = param_gui.data_with_gui.callbacks.on_exit
            if param_on_exit is not None:
                param_on_exit()

    def on_fiat_attributes_changed(self, attrs: FiatAttributes) -> None:
        self._fiat_attributes = attrs
        for param_gui in self._parameters_with_gui:
            prefix = f"{param_gui.name}__"
            this_param_attrs = FiatAttributes({})
            for k, v in attrs.items():
                if k.startswith(prefix):
                    this_param_attrs[k[len(prefix) :]] = v
            if len(this_param_attrs) > 0:
                param_gui.data_with_gui.merge_fiat_attributes(this_param_attrs)

        self._handle_generic_attrs()

    def on_heartbeat(self) -> bool:
        changed = False

        for param_gui in self._parameters_with_gui:
            param_gui.data_with_gui.label_color = get_fiat_config().style.color_as_vec4(
                FiatColorType.DataclassMemberName
            )
            param_on_heartbeat = param_gui.data_with_gui.callbacks.on_heartbeat
            if param_on_heartbeat is not None:
                if param_on_heartbeat():
                    changed = True
        return changed

    def clipboard_copy_str(self, value: DataclassLikeType) -> str:
        strs = {}
        for param_gui in self._parameters_with_gui:
            param_value = getattr(value, param_gui.name)
            param_str = param_gui.data_with_gui.datatype_value_to_clipboard_str(param_value)
            strs[param_gui.name] = param_str
        joined_strs = ", ".join(f"{k}: {v}" for k, v in strs.items())
        r = f"{{{joined_strs}}}"
        return r

    class _Gui_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            GUI
        # ------------------------------------------------------------------------------------------------------------------
        """

    def present(self, _: DataclassLikeType) -> None:
        # the parameter is not used, because we have the data in self._parameters_with_gui
        with imgui_ctx.begin_vertical("##DataclassLikeGui_present"):
            for param_gui in self._parameters_with_gui:
                with imgui_ctx.push_obj_id(param_gui):
                    param_gui.data_with_gui.gui_present_customizable(
                        GuiHeaderLineParams(show_clipboard_button=False, parent_name=self.datatype_basename())
                    )

    def edit(self, original_value: DataclassLikeType) -> tuple[bool, DataclassLikeType]:
        # the parameter is not used, because we have the data in self._parameters_with_gui
        changed = False

        for param_gui in self._parameters_with_gui:
            with imgui_ctx.push_obj_id(param_gui):
                changed_in_edit = param_gui.data_with_gui.gui_edit_customizable(
                    GuiHeaderLineParams(show_clipboard_button=False, parent_name=self.datatype_basename())
                )
                if changed_in_edit:
                    changed = True

        if changed:
            r = self.factor_dataclass_instance_with_edited_values()
            if isinstance(r, (Error, Unspecified)):
                # This should not happen, because we have checked for Unspecified and Error values
                return False, original_value
            elif isinstance(r, Invalid):
                # this can happen with BaseModel when the validation fails
                # we will transmit only when it is ok
                return True, r  # type: ignore
            else:
                return True, r
        else:
            return False, original_value

    class _Serialization_Section:  # Dummy class to create a section in the IDE # noqa
        """
        # ------------------------------------------------------------------------------------------------------------------
        #            Serialization
        # ------------------------------------------------------------------------------------------------------------------
        """

    def save_gui_options_to_json(self) -> JsonDict:
        # We only save the GUI options, not the data!
        return {
            param_gui.name: param_gui.data_with_gui.call_save_gui_options_to_json()
            for param_gui in self._parameters_with_gui
        }

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        # We only load the GUI options, not the data!
        for param_gui in self._parameters_with_gui:
            param_gui.data_with_gui.call_load_gui_options_from_json(json[param_gui.name])
