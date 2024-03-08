from fiatlight.computer_vision.cv_color_type import ColorConversion, ColorType
from fiatlight.core import AnyDataGuiHandlers
from imgui_bundle import imgui_ctx, imgui
from fiatlight import IconsFontAwesome6
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


def make_color_conversion_gui_handlers() -> AnyDataGuiHandlers[ColorConversion]:
    r = AnyDataGuiHandlers[ColorConversion]()

    show_edit_details = False

    def edit(x: ColorConversion) -> Tuple[bool, ColorConversion]:
        nonlocal show_edit_details
        imgui.text(str(x))
        imgui.same_line()
        icon = IconsFontAwesome6.ICON_SQUARE_CARET_UP if show_edit_details else IconsFontAwesome6.ICON_SQUARE_CARET_DOWN
        if imgui.button(icon):
            show_edit_details = not show_edit_details
        if show_edit_details:
            changed, x = gui_color_conversion(x)
            return changed, x
        else:
            return False, x

    r.gui_edit_impl = edit
    r.gui_present_impl = lambda x: imgui.text(str(x))
    r.default_value_provider = lambda: ColorConversion(ColorType.BGR, ColorType.RGB)
    return r
