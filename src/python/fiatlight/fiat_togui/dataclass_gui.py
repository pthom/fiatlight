"""DataclassGui: adds a GUI to a dataclass, or to a pydantic model

Usage example

1. Register the dataclass or pydantic model with `register_dataclass`:
* With pydantic:
    from pydantic import BaseModel

    class MyParam(BaseModel):
        image_in: ImagePath
        image_out: ImagePath_Save = "save.png"  # type: ignore
        x: int | None = None
        y: str = "Hello"

    from fiatlight.fiat_togui import register_dataclass
    register_dataclass(MyParam)


* With dataclasses:
    from dataclasses import dataclass

    @dataclass
    class MyParam:
        image_in: ImagePath
        image_out: ImagePath_Save = "save.png"  # type: ignore
        x: int | None = None
        y: str = "Hello"

    from fiatlight.fiat_togui import register_dataclass
    register_dataclass(MyParam)

2. Use the dataclass in a function:
    def f(param: MyParam) -> MyParam:
        return param

    fiatlight.run(f)
"""

from fiatlight.fiat_core import AnyDataWithGui, FunctionWithGui, ParamWithGui
from fiatlight.fiat_core.any_data_with_gui import GuiHeaderLineParams
from fiatlight.fiat_types import JsonDict, Unspecified, Error
from fiatlight.fiat_core.togui_exception import FiatToGuiException
from fiatlight.fiat_types.base_types import CustomAttributesDict
from imgui_bundle import imgui_ctx, ImVec4
from typing import Type, Any, TypeVar, List
from dataclasses import is_dataclass
from pydantic import BaseModel


# A type variable that represents a dataclass type, or a pydantic BaseModel type
DataclassLikeType = TypeVar("DataclassLikeType")


class DataclassLikeGui(AnyDataWithGui[DataclassLikeType]):
    """Base GUI class for a dataclass or a pydantic model"""

    _parameters_with_gui: List[ParamWithGui[Any]]

    def __init__(
        self, dataclass_type: Type[DataclassLikeType], param_attrs: CustomAttributesDict | None = None
    ) -> None:
        super().__init__(dataclass_type)

        # In order to find the members of the dataclass, we
        # create a FunctionWithGui instance with the dataclass type
        # so that FunctionWithGui can find the members of the dataclass
        # and associate them with GUI
        constructor_gui = FunctionWithGui(dataclass_type, custom_attributes=param_attrs)
        self._parameters_with_gui = constructor_gui._inputs_with_gui

        # We set the _can_set_unspecified_or_default to False for all parameters
        for parameters_with_gui in self._parameters_with_gui:
            parameters_with_gui.data_with_gui._can_set_unspecified_or_default = False
            parameters_with_gui.data_with_gui.label_color = self._member_label_color()

        self.fill_callbacks()
        if param_attrs is not None:
            self.on_custom_attrs_changed(param_attrs)

    def param_of_name(self, name: str) -> ParamWithGui[Any]:
        for param_gui in self._parameters_with_gui:
            if param_gui.name == name:
                return param_gui
        raise ValueError(f"Parameter {name} not found")

    def fill_callbacks(self) -> None:
        self.callbacks.present_str = self.present_str
        self.callbacks.present = self.present

        # It is always possible to present and edit a dataclass in a popup
        self.callbacks.edit_popup_possible = True
        self.callbacks.present_popup_possible = True

        # A popup is required only if any of the parameters require a popup
        self.callbacks.present_popup_required = False
        self.callbacks.edit_popup_required = False
        for param_gui in self._parameters_with_gui:
            if param_gui.data_with_gui.callbacks.present_popup_required:
                self.callbacks.present_popup_required = True
            if param_gui.data_with_gui.callbacks.edit_popup_required:
                self.callbacks.edit_popup_required = True

        self.callbacks.edit_collapsible = True
        self.callbacks.present_collapsible = True

        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.on_exit = self.on_exit
        self.callbacks.on_heartbeat = self.on_heartbeat

        self.callbacks.clipboard_copy_str = None
        self.callbacks.clipboard_copy_possible = False

        self.callbacks.default_value_provider = self.default_value_provider

        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

        self.callbacks.on_custom_attrs_changed = self.on_custom_attrs_changed

    def is_fully_specified(self) -> bool:
        has_unspecified = False
        for param_gui in self._parameters_with_gui:
            param_value = param_gui.data_with_gui.value
            if isinstance(param_value, (Unspecified, Error)):
                has_unspecified = True
                break
        return not has_unspecified

    def factor_dataclass_instance(self) -> DataclassLikeType:
        kwargs = {}
        for param_gui in self._parameters_with_gui:
            param_value = param_gui.data_with_gui.value
            if isinstance(param_value, (Unspecified, Error)):
                raise ValueError(f"Parameter {param_gui.name} is unspecified")
            kwargs[param_gui.name] = param_value
        r = self._type(**kwargs)
        return r

    def default_value_provider(self) -> DataclassLikeType:
        for param_gui in self._parameters_with_gui:
            if not isinstance(param_gui.default_value, Unspecified):
                param_gui.data_with_gui.value = param_gui.default_value
            else:
                default_value_provider = param_gui.data_with_gui.callbacks.default_value_provider
                if default_value_provider is None:
                    raise ValueError(f"Parameter {param_gui.name} has no default value provider")
                param_gui.data_with_gui.value = default_value_provider()

        r = self.factor_dataclass_instance()
        return r

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

    def on_custom_attrs_changed(self, attrs: CustomAttributesDict) -> None:
        self._custom_attrs = attrs
        for param_gui in self._parameters_with_gui:
            prefix = f"{param_gui.name}__"
            this_param_attrs = CustomAttributesDict({})
            for k, v in attrs.items():
                if k.startswith(prefix):
                    this_param_attrs[k[len(prefix) :]] = v
            if len(this_param_attrs) > 0:
                param_gui.data_with_gui.merge_custom_attrs(this_param_attrs)

    def on_heartbeat(self) -> bool:
        changed = False
        for param_gui in self._parameters_with_gui:
            param_on_heartbeat = param_gui.data_with_gui.callbacks.on_heartbeat
            if param_on_heartbeat is not None:
                if param_on_heartbeat():
                    changed = True
        return changed

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
        with imgui_ctx.begin_vertical("##CompositeGui_present"):
            for param_gui in self._parameters_with_gui:
                with imgui_ctx.push_obj_id(param_gui):
                    param_gui.data_with_gui.gui_present_customizable(GuiHeaderLineParams(show_clipboard_button=False))

    def edit(self, value: DataclassLikeType) -> tuple[bool, DataclassLikeType]:
        changed = False

        for param_gui in self._parameters_with_gui:
            with imgui_ctx.push_obj_id(param_gui):
                if not hasattr(value, param_gui.name):
                    raise ValueError(f"Object does not have attribute {param_gui.name}")
                param_gui.data_with_gui.value = getattr(value, param_gui.name)
                changed_in_edit = param_gui.data_with_gui.gui_edit_customizable(
                    GuiHeaderLineParams(show_clipboard_button=False)
                )
                if changed_in_edit:
                    new_value = param_gui.data_with_gui.value
                    setattr(value, param_gui.name, new_value)
                    changed = True

        if changed:
            r = self.factor_dataclass_instance()
            return changed, r
        else:
            return False, value

    def _member_label_color(self) -> ImVec4:
        from fiatlight.fiat_config import get_fiat_config, FiatColorType

        r = get_fiat_config().style.color_as_vec4(FiatColorType.DataclassMemberName)
        return r

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

    def __init__(self, dataclass_type: Type[DataclassLikeType], param_attrs: dict[str, Any] | None = None) -> None:
        if not is_dataclass(dataclass_type):
            raise FiatToGuiException(f"{dataclass_type} is not a dataclass")

        super().__init__(dataclass_type, param_attrs)  # type: ignore


class BaseModelGui(DataclassLikeGui[DataclassLikeType]):
    """A sophisticated GUI for a pydantic model. Can edit and present all members of the model. Can handle nested models."""

    def __init__(
        self, basemodel_type: Type[DataclassLikeType], param_attrs: CustomAttributesDict | None = None
    ) -> None:
        if not issubclass(basemodel_type, BaseModel):
            raise FiatToGuiException(f"{basemodel_type} is not a pydantic model")
        super().__init__(basemodel_type, param_attrs)  # type: ignore
        self.callbacks.load_from_dict = self._load_from_dict
        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str

        # Look for fields with default_factory
        self._initialize_fields()

    def _initialize_fields(self) -> None:
        basemodel_type = self._type
        assert issubclass(basemodel_type, BaseModel)
        for field_name, model_field in basemodel_type.model_fields.items():
            param = self.param_of_name(field_name)
            if model_field.default_factory:
                param.default_value = model_field.default_factory()
                param.data_with_gui.callbacks.default_value_provider = model_field.default_factory

    @staticmethod
    def _save_to_dict(value: DataclassLikeType) -> JsonDict:
        r = {"type": "Pydantic", "value": value.model_dump(mode="json")}  # type: ignore
        return r

    def _load_from_dict(self, json_data: JsonDict) -> DataclassLikeType:
        json_data_type = json_data.get("type")
        if json_data_type != "Pydantic":
            raise ValueError(f"Expected type Pydantic, got {json_data_type}")
        assert self._type is not None
        assert issubclass(self._type, BaseModel)
        r = self._type.model_validate(json_data["value"])
        assert isinstance(r, self._type)
        return r  # type: ignore

    def clipboard_copy_str(self, value: DataclassLikeType) -> str:
        assert isinstance(value, BaseModel)
        return value.model_dump_json(indent=2)
