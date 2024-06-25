from typing import Any

from imgui_bundle import immapp, hello_imgui, imgui, ImVec2, imgui_ctx  # noqa
from pydantic import BaseModel, Field  # noqa
import fiatlight as fl
import logging


def validate_odd_number(x: int) -> int:
    if x % 2 == 0:
        raise ValueError("Must be odd")
    return x


@fl.base_model_with_gui_registration(x__range=(0, 10), x__validator=validate_odd_number)
class MyParam(BaseModel):
    x: int = 3


def edit_value_with_gui(label: str, value_with_gui: fl.AnyDataWithGui[Any]) -> bool:
    with imgui_ctx.push_obj_id(value_with_gui):
        imgui.text("Edit " + label)
        changed = value_with_gui.gui_edit()
        if changed:
            logging.info("changed")
        imgui.text("-------------")
        imgui.text("Present " + label)
        value_with_gui.gui_present()
        imgui.separator()
        return changed


def main() -> None:
    my_param_with_gui = fl.fiat_togui.to_data_with_gui(MyParam())
    my_param_with_gui._can_set_unspecified_or_default = True
    # my_param_with_gui.add_validator_callback(odd_validator)

    def gui() -> None:
        with imgui_ctx.begin_vertical("main"):
            imgui.dummy(ImVec2(500, 10))
            edit_value_with_gui("my_param_with_gui", my_param_with_gui)

        from fiatlight.fiat_widgets import fiat_osd

        fiat_osd.render_all_osd()

    hello_imgui.run(gui)


main()
