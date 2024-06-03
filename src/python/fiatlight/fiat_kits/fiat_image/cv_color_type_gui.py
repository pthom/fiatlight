from fiatlight.fiat_kits.fiat_image.cv_color_type import ColorConversion, ColorType
from fiatlight.fiat_core import AnyDataWithGui
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


class ColorConversionWithGui(AnyDataWithGui[ColorConversion]):
    """A Gui for editing a ColorConversion object."""

    def __init__(self) -> None:
        super().__init__(ColorConversion)
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: ColorConversion(ColorType.BGR, ColorType.RGB)

    @staticmethod
    def edit(value: ColorConversion) -> tuple[bool, ColorConversion]:
        imgui.text(str(value))
        imgui.same_line()
        changed, value = gui_color_conversion(value)
        return changed, value


def sandbox() -> None:
    from fiatlight.fiat_kits.fiat_image.lut_functions import LutParams

    def f(conversion: ColorConversion, lut_param: LutParams) -> str:
        return str(conversion) + " - " + str(lut_param)

    import fiatlight

    fiatlight.run(f)


if __name__ == "__main__":
    sandbox()
