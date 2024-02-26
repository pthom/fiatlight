from fiatlight.computer_vision.cv_color_type import ColorConversion, ColorType
from fiatlight.any_data_with_gui import AnyDataWithGui, Unspecified, UnspecifiedValue
from imgui_bundle import imgui_ctx, imgui
from typing import Tuple


def gui_color_conversion(color_conversion: ColorConversion) -> Tuple[bool, ColorConversion]:
    changed = False
    available_src_colors = ColorType.all_color_types()
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


class ConvertColorWithGui(AnyDataWithGui[ColorConversion]):
    def __init__(self, value: ColorConversion | Unspecified = UnspecifiedValue) -> None:
        def edit_gui() -> bool:
            assert isinstance(self.value, ColorConversion)
            changed, self.value = gui_color_conversion(self.value)
            return changed

        def present_gui() -> None:
            assert isinstance(self.value, ColorConversion)
            imgui.text(str(self.value))

        super().__init__(value, present_gui, edit_gui)
