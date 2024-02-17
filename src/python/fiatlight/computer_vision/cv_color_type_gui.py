from fiatlight.computer_vision.cv_color_type import ColorConversion, ColorType, OptionalColorConversion
from imgui_bundle import imgui_ctx, imgui
from numpy.typing import NDArray
from typing import Any, Tuple


def gui_color_conversion(
    color_conversion: OptionalColorConversion, input_image: NDArray[Any]
) -> Tuple[bool, OptionalColorConversion]:
    if color_conversion is None:
        color_conversion = ColorConversion.make_default_color_conversion(input_image)
    if color_conversion is None:
        return False, None

    changed = False
    available_src_colors = ColorType.available_color_types_for_image(input_image)
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
