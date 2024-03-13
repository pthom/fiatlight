from fiatlight.computer_vision.cv_color_type import ColorConversion, ColorType
from fiatlight.core import AnyDataWithGui
from imgui_bundle import imgui_ctx, imgui, icons_fontawesome_4
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


class ColorConversionWithGui(AnyDataWithGui[ColorConversion]):
    show_edit_details: bool = False

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.present = self.present
        self.callbacks.default_value_provider = lambda: ColorConversion(ColorType.BGR, ColorType.RGB)

    def present(self) -> None:
        imgui.text(str(self.get_actual_value()))

    def edit(self) -> bool:
        value = self.get_actual_value()

        imgui.text(str(value))
        imgui.same_line()
        icon = (
            icons_fontawesome_4.ICON_FA_CARET_UP if self.show_edit_details else icons_fontawesome_4.ICON_FA_CARET_DOWN
        )
        if imgui.button(icon):
            self.show_edit_details = not self.show_edit_details
        if self.show_edit_details:
            changed, value = gui_color_conversion(value)
            return changed
        else:
            return False
