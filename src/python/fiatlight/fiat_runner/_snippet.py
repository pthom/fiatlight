import fiatlight
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from imgui_bundle import imgui_ctx, imgui, ImVec4, hello_imgui, ImVec2


def to_fahrenheit(celsius: float = 10) -> float:
    return celsius * 9 / 5 + 32


# We transform the function to a function with a GUI
to_fahrenheit_gui = fiatlight.FunctionWithGui(to_fahrenheit)


# We define a custom GUI for the celsius parameter
def edit_celsius(celsius: float) -> tuple[bool, float]:
    """Edit the celsius value with a slider, with a blue and red circle icon on each side."""
    with imgui_ctx.begin_horizontal("fahrenheit"):
        with fontawesome_6_ctx():
            with imgui_ctx.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(0, 0)):
                imgui.text_colored(ImVec4(0, 0, 1, 1), icons_fontawesome_6.ICON_FA_CIRCLE)
                imgui.set_next_item_width(hello_imgui.em_size(6))
                changed, celsius = imgui.slider_float("##Celsius", celsius, -20, 60)
                imgui.text_colored(ImVec4(1, 0, 0, 1), icons_fontawesome_6.ICON_FA_CIRCLE)
                imgui.text("°C")
    return changed, celsius


# We set the custom GUI for the celsius parameter
to_fahrenheit_gui.input("celsius").set_edit_callback(edit_celsius)

# And we run the function with the GUI
fiatlight.fiat_run(to_fahrenheit_gui)
