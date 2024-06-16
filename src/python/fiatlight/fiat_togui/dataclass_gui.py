"""DataclassGui: adds a GUI to a dataclass

Usage example
=============

**Register the dataclass**

_Either with the decorator `@fl.dataclass_with_gui_registration`:_

    import fiatlight as fl

    @fl.dataclass_with_gui_registration(x__range=(0, 10))
    class MyParam:
        image_in: ImagePath
        x: int | None = None

_Or with `register_dataclass`:_

    from dataclasses import dataclass

    @dataclass
    class MyParam:
        image_in: ImagePath
        x: int | None = None

    from fiatlight.fiat_togui import register_dataclass
    register_dataclass(MyParam, x__range=(0, 10))

**Use the dataclass in a function:**

    def f(param: MyParam) -> MyParam:
        return param

    fiatlight.run(f)
"""

from fiatlight.fiat_core import AnyDataWithGui, FunctionWithGui, ParamWithGui
from fiatlight.fiat_core.any_data_with_gui import GuiHeaderLineParams
from fiatlight.fiat_types import JsonDict, Unspecified, Error
from fiatlight.fiat_core.togui_exception import FiatToGuiException
from fiatlight.fiat_types.base_types import FiatAttributes
from imgui_bundle import imgui_ctx, ImVec4
from typing import Type, Any, TypeVar, List
from dataclasses import is_dataclass

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
        constructor_gui = FunctionWithGui(dataclass_type, fiat_attributes=fiat_attributes)
        self._parameters_with_gui = constructor_gui._inputs_with_gui

        # We set the _can_set_unspecified_or_default to False for all parameters
        for parameters_with_gui in self._parameters_with_gui:
            parameters_with_gui.data_with_gui._can_set_unspecified_or_default = False
            parameters_with_gui.data_with_gui.label_color = self._member_label_color()

        self.fill_callbacks()
        if fiat_attributes is not None:
            self.on_fiat_attributes_changed(fiat_attributes)

    def fill_callbacks(self) -> None:
        self.callbacks.present_str = self.present_str
        self.callbacks.present = self.present
        self.callbacks.edit = self.edit

        # It is always possible to collapse a dataclass
        self.callbacks.edit_collapsible = True
        self.callbacks.present_collapsible = True

        # The data cannot be presented in a node if any of its params is incompatible
        self.callbacks.present_node_compatible = True
        self.callbacks.edit_node_compatible = True
        for param_gui in self._parameters_with_gui:
            if not param_gui.data_with_gui.callbacks.present_node_compatible:
                self.callbacks.present_node_compatible = False
            if not param_gui.data_with_gui.callbacks.edit_node_compatible:
                self.callbacks.edit_node_compatible = False

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

    def factor_dataclass_instance(self) -> DataclassLikeType | Error:
        kwargs = {}
        for param_gui in self._parameters_with_gui:
            param_value = param_gui.data_with_gui.value
            if isinstance(param_value, (Unspecified, Error)):
                raise ValueError(f"Parameter {param_gui.name} is unspecified in class {self._type}")
            kwargs[param_gui.name] = param_value
        r = self._type(**kwargs)
        return r

    def default_value_provider(self) -> DataclassLikeType:
        for param_gui in self._parameters_with_gui:
            if not isinstance(param_gui.default_value, Unspecified):
                param_gui.data_with_gui.value = param_gui.default_value
            else:
                if not param_gui.data_with_gui.can_construct_default_value():
                    raise ValueError(f"Parameter {param_gui.name} has no default value provider in class {self._type}")
                param_gui.data_with_gui.value = param_gui.data_with_gui.construct_default_value()

        default_value = self.factor_dataclass_instance()
        if isinstance(default_value, Error):
            raise ValueError(
                f"""
            DataclassLikeGui({self.datatype_name()}).default_value_provider
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

    def sub_items_collapse_or_expand(self, collapse_or_expand: AnyDataWithGui.CollapseOrExpand) -> None:
        from fiatlight.fiat_togui.composite_gui import TupleWithGui

        new_expanded_state = collapse_or_expand == AnyDataWithGui.CollapseOrExpand.expand

        for param_gui in self._parameters_with_gui:
            if param_gui.data_with_gui.callbacks.present_collapsible:
                param_gui.data_with_gui._expanded = new_expanded_state
                if isinstance(param_gui.data_with_gui, (DataclassLikeGui, TupleWithGui)):
                    param_gui.data_with_gui.sub_items_collapse_or_expand(collapse_or_expand)

    def sub_items_will_collapse_or_expand(
        self, present_or_edit: AnyDataWithGui.PresentOrEdit
    ) -> AnyDataWithGui.CollapseOrExpand:
        for param_gui in self._parameters_with_gui:
            if (
                param_gui.data_with_gui.callbacks.present_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.present
                and param_gui.data_with_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpand.collapse
            if (
                param_gui.data_with_gui.callbacks.edit_collapsible
                and present_or_edit == AnyDataWithGui.PresentOrEdit.edit
                and param_gui.data_with_gui._expanded
            ):
                return AnyDataWithGui.CollapseOrExpand.collapse
        return AnyDataWithGui.CollapseOrExpand.expand

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

    def on_heartbeat(self) -> bool:
        changed = False
        for param_gui in self._parameters_with_gui:
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

    def present_str(self, _: DataclassLikeType) -> str:
        # the parameter is not used, because we have the data in the self._parameters_with_gui
        strs: dict[str, str] = {}
        for param_gui in self._parameters_with_gui:
            param_value = param_gui.data_with_gui.value
            assert not isinstance(param_value, (Error, Unspecified))
            param_str = param_gui.data_with_gui.datatype_value_to_str(param_value)
            strs[param_gui.name] = param_str
        joined_strs = ", ".join(f"{k}: {v}" for k, v in strs.items())
        r = f"{self._type.__name__}({joined_strs})"
        return r

    def present(self, _: DataclassLikeType) -> None:
        # the parameter is not used, because we have the data in self._parameters_with_gui
        with imgui_ctx.begin_vertical("##DataclassLikeGui_present"):
            for param_gui in self._parameters_with_gui:
                with imgui_ctx.push_obj_id(param_gui):
                    param_gui.data_with_gui.gui_present_customizable(
                        GuiHeaderLineParams(show_clipboard_button=False, parent_name=self.datatype_name())
                    )

    def edit(self, value: DataclassLikeType) -> tuple[bool, DataclassLikeType]:
        changed = False

        for param_gui in self._parameters_with_gui:
            with imgui_ctx.push_obj_id(param_gui):
                if not hasattr(value, param_gui.name):
                    raise ValueError(f"Object does not have attribute {param_gui.name}")
                param_gui.data_with_gui.value = getattr(value, param_gui.name)
                changed_in_edit = param_gui.data_with_gui.gui_edit_customizable(
                    GuiHeaderLineParams(show_clipboard_button=False, parent_name=self.datatype_name())
                )
                if changed_in_edit:
                    new_value = param_gui.data_with_gui.value
                    setattr(value, param_gui.name, new_value)
                    changed = True

        if changed:
            r = self.factor_dataclass_instance()
            if isinstance(r, Error):
                raise RuntimeError(
                    f"""
                DataclassLikeGui({self.datatype_name()}).edit() called factor_dataclass_instance()
                which returned an error.
                This is not allowed. The subtypes (such as BaseModelGui) should
                catch the error, store the values as invalid value in self._parameters_with_gui
                and return the correct type anyhow
                """
                )
            return changed, r
        else:
            return False, value

    @staticmethod
    def _member_label_color() -> ImVec4:
        from fiatlight.fiat_config import get_fiat_config, FiatColorType

        r = get_fiat_config().style.color_as_vec4(FiatColorType.DataclassMemberName)
        return r

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


class DataclassGui(DataclassLikeGui[DataclassLikeType]):
    """A sophisticated GUI for a dataclass type. Can edit and present all members of the dataclass. Can handle nested dataclasses."""

    def __init__(self, dataclass_type: Type[DataclassLikeType], fiat_attributes: dict[str, Any] | None = None) -> None:
        if not is_dataclass(dataclass_type):
            raise FiatToGuiException(f"{dataclass_type} is not a dataclass")

        super().__init__(dataclass_type, fiat_attributes)  # type: ignore
