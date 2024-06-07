from typing import Any

from imgui_bundle import immapp, hello_imgui, imgui, ImVec2, imgui_ctx  # noqa
from pydantic import BaseModel, Field
import fiatlight as fl
import logging


@fl.base_model_with_gui_registration(
    a__range=(0, 10),
    c__range=(0, 10),
)
class InnerParam(BaseModel):
    a: int = 1
    b: str = "World"
    c: float = 2.71


@fl.base_model_with_gui_registration(
    x__range=(0, 10),
    z__range=(0, 10),
)
class MyParam(BaseModel):
    inner: InnerParam = Field(default_factory=InnerParam)
    x: int = 3
    y: str = "Hello"
    z: float = 3.14


def edit_value_with_gui(value_with_gui: fl.AnyDataWithGui[Any]) -> bool:
    with imgui_ctx.push_obj_id(value_with_gui):
        _, value_with_gui._can_set_unspecified = imgui.checkbox(
            "_can_set_unspecified", value_with_gui._can_set_unspecified
        )
        changed = value_with_gui.gui_edit()
        if changed:
            logging.info("changed")
        return changed


def usability_int_with_gui() -> None:
    from fiatlight.fiat_togui import IntWithGui, StrWithGui

    int_with_gui = IntWithGui()
    int_with_gui._can_set_unspecified = True
    int_with_gui.value = 2
    int_with_gui.add_validate_value_callback(
        lambda x: (fl.DataValidationResult.ok() if x % 2 == 0 else fl.DataValidationResult.error("Must be even"))
    )

    str_with_gui = StrWithGui()
    str_with_gui._can_set_unspecified = True
    # str_with_gui.value = "Hello"
    str_with_gui.add_validate_value_callback(
        lambda x: (
            fl.DataValidationResult.ok()
            if len(x) < 5
            else fl.DataValidationResult.error("Must be shorter than 5 chars")
        )
    )

    my_param_with_gui = fl.fiat_togui.any_type_to_gui(MyParam, {})
    my_param_with_gui._can_set_unspecified = True
    # my_param_with_gui.value = MyParam()
    my_param_with_gui.add_validate_value_callback(
        lambda x: (
            fl.DataValidationResult.ok() if x.x % 2 == 1 else fl.DataValidationResult.error("MyParam.x must be odd")
        )
    )

    def gui() -> None:
        with imgui_ctx.begin_vertical("main", ImVec2(500, 1)):
            imgui.dummy(ImVec2(500, 10))
            imgui.text("IntWithGui")
            edit_value_with_gui(int_with_gui)
            imgui.text("StrWithGui")
            edit_value_with_gui(str_with_gui)
            imgui.text("MyParam")
            edit_value_with_gui(my_param_with_gui)

    hello_imgui.run(gui)


usability_int_with_gui()
