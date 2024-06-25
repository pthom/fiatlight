from typing import Any

from imgui_bundle import immapp, hello_imgui, imgui, ImVec2, imgui_ctx  # noqa
from pydantic import BaseModel, Field  # noqa
from enum import Enum
import fiatlight as fl
import logging


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


def odd_validator(x: MyParam) -> MyParam:
    if x.x % 2 == 0:
        raise ValueError("Must be odd")
    return x


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

    int_with_gui = any_type_to_gui(int)
    int_with_gui._can_set_unspecified_or_default = True
    int_with_gui.value = 2

    def even_validator(x: int) -> int:
        if x % 2 != 0:
            raise ValueError("Must be even")
        return x

    int_with_gui.add_validator_callback(even_validator)

    def validate_short_string(s: str) -> str:
        if len(s) >= 5:
            raise ValueError("Must be shorter than 5 chars")
        return s

    str_with_gui = any_type_to_gui(str)
    str_with_gui._can_set_unspecified_or_default = True
    # str_with_gui.value = "Hello"
    str_with_gui.add_validator_callback(validate_short_string)

    my_param_with_gui = fl.fiat_togui.any_type_to_gui(MyParam)
    my_param_with_gui._can_set_unspecified_or_default = True
    # my_param_with_gui.value = MyParam()
    my_param_with_gui.add_validator_callback(odd_validator)

    def gui() -> None:
        with imgui_ctx.begin_vertical("main"):
            imgui.dummy(ImVec2(500, 10))
            edit_value_with_gui("int_with_gui", int_with_gui)
            edit_value_with_gui("str_with_gui", str_with_gui)
            edit_value_with_gui("my_param_with_gui", my_param_with_gui)

    hello_imgui.run(gui)


usability_int_with_gui()
