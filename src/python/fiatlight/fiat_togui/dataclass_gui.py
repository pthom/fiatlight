import logging

from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_types import DataType, JsonDict
from fiatlight.fiat_togui import to_gui
from imgui_bundle import imgui, imgui_ctx, hello_imgui, ImVec2  # noqa
from typing import Type, Any, Callable, TypeVar
from dataclasses import is_dataclass


# A type variable that represents a data type, included in a AnyDataWithGui object.
DataclassType = TypeVar("DataclassType")


class DataclassGui(AnyDataWithGui[DataclassType]):
    parameters_with_gui: dict[str, AnyDataWithGui[Any]]
    _dataclass_type: Type[DataclassType]

    def __init__(self, secret: int) -> None:
        if secret != 42:
            raise ValueError(
                "You are not allowed to create a DataclassGui directly. Use from_parameters_with_gui instead."
            )
        super().__init__()
        self.parameters_with_gui = {}

    @staticmethod
    def from_dataclass_type(
        dataclass_type: Type[DataclassType], default_provider: Callable[[], DataclassType] | None = None
    ) -> "DataclassGui[DataclassType]":
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} is not a dataclass")

        scope_storage = to_gui._capture_current_scope()

        """
        Note:
        It would also be possible to get the field list by inspecting the signature of the constructor.
        This approach would be more generic and not limited to dataclasses.
        But we might lose some advantages of data classes.
            # Get the signature of the dataclass constructor
            signature = inspect.signature(dataclass_type.__init__)
            parameters = signature.parameters
            for name, param in parameters.items():
                if name == "self":  # Skip 'self' parameter
                    continue
                print(f"Parameter name: {name}, type: {param.annotation}")
        """

        parameters_with_gui = {}
        for field in dataclass_type.__dataclass_fields__.values():  # noqa
            is_public = not field.name.startswith("_")
            if is_public:
                field_type = field.type
                parameters_with_gui[field.name] = to_gui._any_type_class_name_to_gui(str(field_type), scope_storage)

        def provider_from_default_ctor() -> DataclassType:
            r = dataclass_type()
            return r  # type: ignore

        if default_provider is None:
            default_provider = provider_from_default_ctor

        # Construct the DataclassGui object
        r: DataclassGui[Any] = DataclassGui(42)
        r._dataclass_type = dataclass_type
        r.parameters_with_gui = parameters_with_gui
        r.callbacks.default_value_provider = default_provider
        r.fill_callbacks()

        return r

    def fill_callbacks(self) -> None:
        logging.info("entering fill_callbacks")
        self.callbacks.present_str = self.present_str
        self.callbacks.present_custom = self.present_custom

        self.callbacks.present_custom_popup_required = False
        self.callbacks.present_custom_popup_required = False
        self.callbacks.edit_popup_possible = False
        self.callbacks.edit_popup_required = False
        for param_gui in self.parameters_with_gui.values():
            if param_gui.callbacks.present_custom_popup_required:
                self.callbacks.present_custom_popup_required = True
            if param_gui.callbacks.present_custom_popup_possible:
                self.callbacks.present_custom_popup_possible = True
            if param_gui.callbacks.edit_popup_possible:
                self.callbacks.edit_popup_possible = True
            if param_gui.callbacks.edit_popup_required:
                self.callbacks.edit_popup_required = True

        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.on_exit = self.on_exit
        self.callbacks.on_heartbeat = self.on_heartbeat

        self.callbacks.clipboard_copy_str = None
        self.callbacks.clipboard_copy_possible = False

        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        logging.info("leaving fill_callbacks")

    def on_change(self, value: DataclassType) -> None:
        for param_name, param_gui in self.parameters_with_gui.items():
            param_on_change = param_gui.callbacks.on_change
            param_value = getattr(value, param_name)
            if param_on_change is not None:
                param_on_change(param_value)

    def on_exit(self) -> None:
        for param_gui in self.parameters_with_gui.values():
            param_on_exit = param_gui.callbacks.on_exit
            if param_on_exit is not None:
                param_on_exit()

    def on_heartbeat(self) -> bool:
        changed = False
        for param_name, param_gui in self.parameters_with_gui.items():
            param_on_heartbeat = param_gui.callbacks.on_heartbeat
            if param_on_heartbeat is not None:
                if param_on_heartbeat():
                    changed = True
        return changed

    def save_gui_options_to_json(self) -> JsonDict:
        r = {}
        for param_name, param_gui in self.parameters_with_gui.items():
            save_gui_options_to_json = param_gui.callbacks.save_gui_options_to_json
            if save_gui_options_to_json is not None:
                r[param_name] = save_gui_options_to_json()
        return r

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        for param_name, param_gui in self.parameters_with_gui.items():
            if param_name in json:
                load_gui_options_from_json = param_gui.callbacks.load_gui_options_from_json
                if load_gui_options_from_json is not None:
                    load_gui_options_from_json(json[param_name])

    def present_str(self, value: DataType) -> str:
        strs: dict[str, str] = {}
        for param_name, param_gui in self.parameters_with_gui.items():
            if not hasattr(value, param_name):
                raise ValueError(f"Object does not have attribute {param_name}")
            param_value = getattr(value, param_name)

            present_str = param_gui.callbacks.present_str
            if present_str is not None:
                strs[param_name] = present_str(param_value)
            else:
                strs[param_name] = str(param_value)
        joined_strs = ", ".join(f"{k}: {v}" for k, v in strs.items())
        r = f"{self._dataclass_type.__name__}({joined_strs})"
        return r

    def present_custom(self, value: DataType) -> None:
        with imgui_ctx.begin_vertical("##CompositeGui_present_custom"):
            for param_name, param_gui in self.parameters_with_gui.items():
                if not hasattr(value, param_name):
                    raise ValueError(f"Object does not have attribute {param_name}")
                param_value = getattr(value, param_name)

                present_custom = param_gui.callbacks.present_custom
                present_str = param_gui.callbacks.present_str

                def fn_present_param() -> None:
                    if present_custom is not None:
                        present_custom(param_value)
                    elif present_str is not None:
                        imgui.text(present_str(param_value))
                    else:
                        imgui.text(str(param_value))

                    imgui.text(param_name)
                    imgui.begin_group()
                    fn_present_param()
                    imgui.end_group()

    def edit(self, value: DataType) -> tuple[bool, DataType]:
        changed = False

        for param_name_, param_gui_ in self.parameters_with_gui.items():
            if not hasattr(value, param_name_):
                raise ValueError(f"Object does not have attribute {param_name_}")

            param_value = getattr(value, param_name_)
            param_edit = param_gui_.callbacks.edit
            param_name_copy = param_name_  # copy to avoid being bound to the loop variable

            def fn_edit_param() -> bool:
                if param_edit is not None:
                    changed_in_edit, new_value = param_edit(param_value)
                    if changed_in_edit:
                        setattr(value, param_name_copy, new_value)
                    return changed_in_edit
                else:
                    imgui.text("No editor")
                    return False

            imgui.text(param_name_copy)
            imgui.same_line()
            imgui.begin_group()
            param_changed = fn_edit_param()
            imgui.end_group()

            if param_changed:
                changed = True

        return changed, value


def make_dataclass_with_gui(
    dataclass_type: Type[DataclassType], default_provider: Callable[[], DataclassType] | None = None
) -> Callable[[], DataclassGui[DataclassType]]:
    def fn() -> DataclassGui[DataclassType]:
        return DataclassGui.from_dataclass_type(dataclass_type, default_provider)

    return fn
