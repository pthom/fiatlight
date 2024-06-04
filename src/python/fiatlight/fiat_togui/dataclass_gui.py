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

import copy

from fiatlight.fiat_core import AnyDataWithGui, FunctionWithGui, ParamWithGui
from fiatlight.fiat_types import JsonDict, Unspecified, Error
from fiatlight.fiat_config import get_fiat_config, FiatColorType
from fiatlight.fiat_widgets import fiat_osd
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import fontawesome_6_ctx
from fiatlight.fiat_widgets import icons_fontawesome_6
from fiatlight.fiat_core.togui_exception import FiatToGuiException
from fiatlight.fiat_types.base_types import CustomAttributesDict
from imgui_bundle import imgui, imgui_ctx, hello_imgui
from typing import Type, Any, TypeVar, List, Callable
from dataclasses import is_dataclass, dataclass
from pydantic import BaseModel


# A type variable that represents a dataclass type, or a pydantic BaseModel type
DataclassLikeType = TypeVar("DataclassLikeType")


@dataclass
class _DrawExpandableMemberResult:
    expanded: bool
    changed: bool


def _draw_expandable_member(
    member_name: str,
    *,
    expanded: bool,
    collapsable: bool,
    fn_gui_expanded: Callable[[], bool] | Callable[[], None],
    fn_gui_collapsed: Callable[[], bool] | Callable[[], None],
) -> _DrawExpandableMemberResult:
    width_align_after = hello_imgui.em_size(5)

    # Draw param name (might be shortened if too long)
    cursor_pos_before_label = imgui.get_cursor_pos()
    member_name_color = get_fiat_config().style.color_as_vec4(FiatColorType.DataclassMemberName)
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

    # Draw expand/collapse button
    if collapsable:
        with fontawesome_6_ctx():
            icon = icons_fontawesome_6.ICON_FA_CARET_DOWN if expanded else icons_fontawesome_6.ICON_FA_CARET_RIGHT
            if imgui.button(icon):
                expanded = not expanded
        imgui.same_line()

    imgui.begin_group()
    if not collapsable:
        changed_or_none = fn_gui_expanded()
    else:
        changed_or_none = fn_gui_expanded() if expanded else fn_gui_collapsed()
    imgui.end_group()

    changed = changed_or_none if isinstance(changed_or_none, bool) else False

    return _DrawExpandableMemberResult(expanded=expanded, changed=changed)


class DataclassLikeGui(AnyDataWithGui[DataclassLikeType]):
    """Base GUI class for a dataclass or a pydantic model"""

    _parameters_with_gui: List[ParamWithGui[Any]]

    # user settings:
    #   Flags that indicate whether the details of the params are shown or not
    #   (those settings are saved in the user settings file)
    _param_expanded: dict[str, bool] = {}

    def __init__(
        self, dataclass_type: Type[DataclassLikeType], param_attrs: CustomAttributesDict | None = None
    ) -> None:
        super().__init__(dataclass_type)
        if param_attrs is not None:
            self._custom_attrs = param_attrs

        constructor_gui = FunctionWithGui(dataclass_type)

        self._parameters_with_gui = constructor_gui._inputs_with_gui
        self.fill_callbacks()
        self._apply_param_attrs()

        self._param_expanded = {}
        for param_gui in self._parameters_with_gui:
            self._param_expanded[param_gui.name] = True

    def param_of_name(self, name: str) -> ParamWithGui[Any]:
        for param_gui in self._parameters_with_gui:
            if param_gui.name == name:
                return param_gui
        raise ValueError(f"Parameter {name} not found")

    def _apply_param_attrs(self) -> None:
        if self._custom_attrs is None:
            return
        for param_gui in self._parameters_with_gui:
            prefix = f"{param_gui.name}__"
            this_param_attrs = {}
            for k, v in self._custom_attrs.items():
                if k.startswith(prefix):
                    this_param_attrs[k[len(prefix) :]] = v
            if len(this_param_attrs) > 0:
                param_gui.data_with_gui.merge_custom_attrs(this_param_attrs)

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
        self._apply_param_attrs()
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
                with imgui_ctx.push_obj_id(param_gui):
                    expand_result = _draw_expandable_member(
                        param_gui.name,
                        collapsable=param_gui.data_with_gui.callbacks.present_custom_collapsible,
                        expanded=self._param_expanded[param_gui.name],
                        fn_gui_expanded=param_gui.data_with_gui.gui_present_custom,
                        fn_gui_collapsed=param_gui.data_with_gui.gui_present_str_one_line,
                    )
                    self._param_expanded[param_gui.name] = expand_result.expanded

    def edit(self, value: DataclassLikeType) -> tuple[bool, DataclassLikeType]:
        changed = False

        for param_gui_ in self._parameters_with_gui:
            with imgui_ctx.push_obj_id(param_gui_):
                if not hasattr(value, param_gui_.name):
                    raise ValueError(f"Object does not have attribute {param_gui_.name}")
                param_gui_.data_with_gui.value = getattr(value, param_gui_.name)

                param_value = param_gui_.data_with_gui.value
                param_edit = param_gui_.data_with_gui.callbacks.edit
                param_name = param_gui_.name  # copy to avoid being bound to the loop variable

                def fn_edit_param() -> bool:
                    if param_edit is None:
                        imgui.text("No editor")
                        return False
                    with imgui_ctx.push_obj_id(param_gui_):
                        changed_in_edit, new_value = param_edit(param_value)
                    if changed_in_edit:
                        param_gui_.data_with_gui.value = new_value
                        setattr(value, param_name, new_value)
                    return changed_in_edit

                expand_result = _draw_expandable_member(
                    param_gui_.name,
                    expanded=self._param_expanded[param_gui_.name],
                    collapsable=param_gui_.data_with_gui.callbacks.edit_collapsible,
                    fn_gui_expanded=fn_edit_param,
                    fn_gui_collapsed=param_gui_.data_with_gui.gui_present_str_one_line,
                )
                self._param_expanded[param_gui_.name] = expand_result.expanded
                if expand_result.changed:
                    changed = True

        if changed:
            r = self.factor_dataclass_instance()
            return changed, r
        else:
            return False, value

    def save_gui_options_to_json(self) -> JsonDict:
        # We only save the GUI options, not the data!
        r = {"param_expanded": self._param_expanded}
        for param_gui in self._parameters_with_gui:
            save_gui_options_to_json = param_gui.data_with_gui.callbacks.save_gui_options_to_json
            if save_gui_options_to_json is not None:
                r[param_gui.name] = save_gui_options_to_json()
        return r

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        # We only load the GUI options, not the data!
        if "param_expanded" in json:
            self._param_expanded = json["param_expanded"]
        for param_gui in self._parameters_with_gui:
            if param_gui.name in json:
                load_gui_options_from_json = param_gui.data_with_gui.callbacks.load_gui_options_from_json
                if load_gui_options_from_json is not None:
                    load_gui_options_from_json(json[param_gui.name])


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
