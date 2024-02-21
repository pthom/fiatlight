from fiatlight.computer_vision.cv_color_type import ColorConversion, ColorType, OptionalColorConversion
from fiatlight import AnyDataWithGui
from imgui_bundle import imgui_ctx, imgui
from typing import Tuple


def gui_color_conversion(color_conversion: OptionalColorConversion) -> Tuple[bool, OptionalColorConversion]:
    changed = False
    available_src_colors = ColorType.all_color_types()
    if color_conversion is None:
        color_conversion = ColorConversion(ColorType.BGR, ColorType.RGB)
    with imgui_ctx.begin_group():
        with imgui_ctx.push_id("source_color"):
            imgui.text("Source color")
            for color in available_src_colors:
                if imgui.radio_button(color.name, color_conversion.src_color == color):
                    color_conversion.src_color = color
                    changed = True

    imgui.same_line()

    available_dst_colors = color_conversion.src_color.available_conversion_outputs()
    with imgui_ctx.begin_group():
        with imgui_ctx.push_id("destination_color"):
            imgui.text("Destination color")
            for color in available_dst_colors:
                if imgui.radio_button(color.name, color_conversion.dst_color == color):
                    color_conversion.dst_color = color
                    changed = True

    return changed, color_conversion


class ConvertColorWithGui(AnyDataWithGui):
    value: ColorConversion | None

    def __init__(self, value: ColorConversion | None = None) -> None:
        def edit_gui(name: str) -> bool:
            imgui.text(name)
            changed, self.value = gui_color_conversion(self.value)
            return changed

        def present_gui(name: str) -> None:
            imgui.text(f"{name}: {self.value}")

        super().__init__(value, present_gui, edit_gui)
