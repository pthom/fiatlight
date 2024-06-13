from typing import Any

from imgui_bundle import immapp, hello_imgui, imgui, ImVec2, imgui_ctx  # noqa
from pydantic import BaseModel, Field  # noqa
from enum import Enum
import fiatlight as fl
import logging


@fl.enum_with_gui_registration
class MyEnum(Enum):
    A = "A"
    B = "B"
    C = "C"


@fl.base_model_with_gui_registration(
    i_c__range=(0, 10),
)
class InnerParam(BaseModel):
    i_enum: MyEnum = MyEnum.A
    i_b: str = "World"
    i_c: float = 2.71


@fl.base_model_with_gui_registration(
    x__range=(0, 10),
    z__range=(0, 10),
)
class MyParam(BaseModel):
    inner: InnerParam = Field(default_factory=InnerParam)
    x: int = 3
    y: str = "Hello"
    z: float = 3.14


def edit_value_with_gui(label: str, value_with_gui: fl.AnyDataWithGui[Any]) -> bool:
    with imgui_ctx.push_obj_id(value_with_gui):
        # _, value_with_gui._can_set_unspecified_or_default = imgui.checkbox(
        #     "_can_set_unspecified_or_default", value_with_gui._can_set_unspecified_or_default
        # )
        imgui.text("Edit " + label)
        changed = value_with_gui.gui_edit()
        if changed:
            logging.info("changed")
        imgui.text("-------------")
        imgui.text("Present " + label)
        value_with_gui.gui_present()
        imgui.separator()
        return changed


def usability_int_with_gui() -> None:
    from fiatlight.fiat_togui import any_type_to_gui

    int_with_gui = any_type_to_gui(int, {})
    int_with_gui._can_set_unspecified_or_default = True
    int_with_gui.value = 2
    int_with_gui.add_validate_value_callback(
        lambda x: (fl.DataValidationResult.ok() if x % 2 == 0 else fl.DataValidationResult.error("Must be even"))
    )

    str_with_gui = any_type_to_gui(str, {})
    str_with_gui._can_set_unspecified_or_default = True
    # str_with_gui.value = "Hello"
    str_with_gui.add_validate_value_callback(
        lambda x: (
            fl.DataValidationResult.ok()
            if len(x) < 5
            else fl.DataValidationResult.error("Must be shorter than 5 chars")
        )
    )

    my_param_with_gui = fl.fiat_togui.any_type_to_gui(MyParam, {})
    my_param_with_gui._can_set_unspecified_or_default = True
    # my_param_with_gui.value = MyParam()
    my_param_with_gui.add_validate_value_callback(
        lambda x: (
            fl.DataValidationResult.ok() if x.x % 2 == 1 else fl.DataValidationResult.error("MyParam.x must be odd")
        )
    )

    def gui() -> None:
        with imgui_ctx.begin_vertical("main"):
            imgui.dummy(ImVec2(500, 10))
            edit_value_with_gui("int_with_gui", int_with_gui)
            edit_value_with_gui("str_with_gui", str_with_gui)
            edit_value_with_gui("my_param_with_gui", my_param_with_gui)

    hello_imgui.run(gui)


usability_int_with_gui()
