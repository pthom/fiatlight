from imgui_bundle import imgui, hello_imgui
from imgui_bundle import icons_fontawesome_6
import logging


_FONT_AWESOME_6: imgui.ImFont | None = None


def _load_font_awesome_6() -> None:
    global _FONT_AWESOME_6
    print("_load_font_awesome_6")
    font_size = 17
    font_params = hello_imgui.FontLoadingParams()
    font_params.use_full_glyph_range = True
    _FONT_AWESOME_6 = hello_imgui.load_font("fonts/Font_Awesome_6_Free-Solid-900.otf", font_size, font_params)


class PushFontAwesome6:
    """Context manager to push the Font Awesome 6 font for the current frame.
    If the font is not loaded, it will be loaded (and will appear on the next frame)"""

    def __init__(self) -> None:
        if _FONT_AWESOME_6 is None:
            # Fonts need to be loaded before the new frame starts,
            hello_imgui.get_runner_params().callbacks.load_additional_fonts = _load_font_awesome_6

    def __enter__(self) -> None:
        if _FONT_AWESOME_6 is not None:
            imgui.push_font(_FONT_AWESOME_6)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        try:
            if _FONT_AWESOME_6 is not None:
                imgui.pop_font()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginEnd context", exc_info=(exc_type, exc_val, exc_tb))


def fontawesome_6_ctx() -> PushFontAwesome6:
    return PushFontAwesome6()


__all__ = ["fontawesome_6_ctx", "icons_fontawesome_6"]
