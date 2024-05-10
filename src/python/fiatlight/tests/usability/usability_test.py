import fiatlight
from imgui_bundle import imgui


def sandbox() -> None:
    def f() -> str:
        return """Hello,
        world!
        YAY!"""

    f_gui = fiatlight.FunctionWithGui(f)

    def my_present_custom_callback(x: str) -> None:
        imgui.text(f"AHHH ==> {x}")

    f_gui.output().set_present_custom_callback(my_present_custom_callback, popup_required=False)
    fiatlight.fiat_run(f_gui)


if __name__ == "__main__":
    sandbox()
