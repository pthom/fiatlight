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

    fiatlight.fiat_run(f)
"""
import copy

from fiatlight import fiat_widgets
from fiatlight.fiat_core import AnyDataWithGui, FunctionWithGui, ParamWithGui
from fiatlight.fiat_types import JsonDict, Unspecified, Error
from fiatlight.fiat_togui import to_gui
from fiatlight.fiat_config import get_fiat_config, FiatColorType
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_ctx, hello_imgui
from typing import Type, Any, TypeVar, List
from dataclasses import is_dataclass
from pydantic import BaseModel


# A type variable that represents a dataclass type, or a pydantic BaseModel type
DataclassLikeType = TypeVar("DataclassLikeType")


def _draw_dataclass_member_name(member_name: str) -> None:
    width_align_after = hello_imgui.em_size(5)

    # Draw param name (might be shortened if too long)
    cursor_pos_before_label = imgui.get_cursor_pos()
    member_name_color = get_fiat_config().style.colors[FiatColorType.DataclassMemberName]
    with imgui_ctx.push_style_color(imgui.Col_.text.value, member_name_color):
        member_name_short = member_name
        while imgui.calc_text_size(member_name_short).x > width_align_after:
            member_name_short = member_name_short[:-1]
        is_too_long = len(member_name_short) < len(member_name)
        if is_too_long:
            member_name_short = member_name_short[:-1] + "..."
        imgui.text(member_name_short)
        if is_too_long:
            fiat_osd.set_widget_tooltip(member_name)

    cursor_pos_after_label = copy.copy(cursor_pos_before_label)
    cursor_pos_after_label.x += width_align_after
    imgui.set_cursor_pos(cursor_pos_after_label)


class DataclassLikeGui(AnyDataWithGui[DataclassLikeType]):
    """Base GUI class for a dataclass or a pydantic model"""

    _parameters_with_gui: List[ParamWithGui[Any]]

    def __init__(self, dataclass_type: Type[DataclassLikeType]) -> None:
        super().__init__(dataclass_type)

        # if not is_dataclass(dataclass_type):
        #     raise ValueError(f"{dataclass_type} is not a dataclass")

        scope_storage = to_gui.capture_current_scope()
        constructor_gui = FunctionWithGui(dataclass_type, scope_storage=scope_storage)

        self._parameters_with_gui = constructor_gui._inputs_with_gui
        self.fill_callbacks()

    def fill_callbacks(self) -> None:
        self.callbacks.present_str = self.present_str
        self.callbacks.present_custom = self.present_custom

        self.callbacks.present_custom_popup_required = False
        self.callbacks.present_custom_popup_required = False
        self.callbacks.edit_popup_possible = False
        self.callbacks.edit_popup_required = False
        for param_gui in self._parameters_with_gui:
            if param_gui.data_with_gui.callbacks.present_custom_popup_required:
                self.callbacks.present_custom_popup_required = True
            if param_gui.data_with_gui.callbacks.present_custom_popup_possible:
                self.callbacks.present_custom_popup_possible = True
            if param_gui.data_with_gui.callbacks.edit_popup_possible:
                self.callbacks.edit_popup_possible = True
            if param_gui.data_with_gui.callbacks.edit_popup_required:
                self.callbacks.edit_popup_required = True

        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.on_exit = self.on_exit
        self.callbacks.on_heartbeat = self.on_heartbeat

        self.callbacks.clipboard_copy_str = None
        self.callbacks.clipboard_copy_possible = False

        self.callbacks.default_value_provider = self.default_value_provider

        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

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

    def present_custom(self, _: DataclassLikeType) -> None:
        # the parameter is not used, because we have the data in self._parameters_with_gui
        with imgui_ctx.begin_vertical("##CompositeGui_present_custom"):
            for param_gui in self._parameters_with_gui:
                param_value = param_gui.data_with_gui.value

                present_custom = param_gui.data_with_gui.callbacks.present_custom
                present_str = param_gui.data_with_gui.callbacks.present_str

                def fn_present_param() -> None:
                    if present_custom is not None:
                        present_custom(param_value)
                    else:
                        as_str: str
                        if present_str is not None:
                            as_str = present_str(param_value)
                        else:
                            as_str = str(param_value)
                        max_width_pixels = hello_imgui.em_size(40)
                        fiat_widgets.text_maybe_truncated(as_str, max_lines=1, max_width_pixels=max_width_pixels)

                _draw_dataclass_member_name(param_gui.name)
                imgui.begin_group()
                fn_present_param()
                imgui.end_group()

    def edit(self, value: DataclassLikeType) -> tuple[bool, DataclassLikeType]:
        changed = False

        for param_gui_ in self._parameters_with_gui:
            with imgui_ctx.push_id(param_gui_.name):
                if not hasattr(value, param_gui_.name):
                    raise ValueError(f"Object does not have attribute {param_gui_.name}")
                param_gui_.data_with_gui.value = getattr(value, param_gui_.name)

                param_value = param_gui_.data_with_gui.value
                param_edit = param_gui_.data_with_gui.callbacks.edit
                param_name = param_gui_.name  # copy to avoid being bound to the loop variable

                def fn_edit_param() -> bool:
                    if param_edit is not None:
                        changed_in_edit, new_value = param_edit(param_value)
                        if changed_in_edit:
                            param_gui_.data_with_gui.value = new_value
                            setattr(value, param_name, new_value)
                        return changed_in_edit
                    else:
                        imgui.text("No editor")
                        return False

                _draw_dataclass_member_name(param_name)
                imgui.begin_group()
                param_changed = fn_edit_param()
                imgui.end_group()

                if param_changed:
                    changed = True

        if changed:
            r = self.factor_dataclass_instance()
            return changed, r
        else:
            return False, value

    def save_gui_options_to_json(self) -> JsonDict:
        # We only save the GUI options, not the data!
        r = {}
        for param_gui in self._parameters_with_gui:
            save_gui_options_to_json = param_gui.data_with_gui.callbacks.save_gui_options_to_json
            if save_gui_options_to_json is not None:
                r[param_gui.name] = save_gui_options_to_json()
        return r

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        # We only load the GUI options, not the data!
        for param_gui in self._parameters_with_gui:
            if param_gui.name in json:
                load_gui_options_from_json = param_gui.data_with_gui.callbacks.load_gui_options_from_json
                if load_gui_options_from_json is not None:
                    load_gui_options_from_json(json[param_gui.name])


class DataclassGui(DataclassLikeGui[DataclassLikeType]):
    def __init__(self, dataclass_type: Type[DataclassLikeType]) -> None:
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} is not a dataclass")

        super().__init__(dataclass_type)  # type: ignore


class BaseModelGui(DataclassLikeGui[DataclassLikeType]):
    def __init__(self, dataclass_type: Type[DataclassLikeType]) -> None:
        if not issubclass(dataclass_type, BaseModel):
            raise ValueError(f"{dataclass_type} is not a pydantic model")
        super().__init__(dataclass_type)  # type: ignore
        self.callbacks.load_from_dict = self._load_from_dict
        self.callbacks.save_to_dict = self._save_to_dict

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
