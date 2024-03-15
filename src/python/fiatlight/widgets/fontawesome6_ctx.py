from imgui_bundle import imgui, hello_imgui
from fiatlight.utils import functional_utils
from imgui_bundle import icons_fontawesome_6
import logging


_FONT_AWESOME_6: imgui.ImFont | None = None


def _load_font_awesome_6():
    global _FONT_AWESOME_6
    if _FONT_AWESOME_6 is not None:
        return

    print("_load_font_awesome_6")
    ft = imgui.get_io().fonts
    font_size = 15
    _FONT_AWESOME_6 = hello_imgui.load_font("fonts/DroidSans.ttf", font_size)
    # font_params = hello_imgui.FontLoadingParams()
    # font_params.merge_to_last_font = True
    # font_params.use_full_glyph_range = True
    # _FONT_AWESOME_6 = hello_imgui.load_font("fonts/Font_Awesome_6_Free-Solid-900.otf", font_size, font_params)
    success = imgui.get_io().fonts.build()
    if not success:
        logging.error("Failed to load Font Awesome 6")
        _FONT_AWESOME_6 = None
    io = imgui.get_io()
    print("a")


class PushFontAwesome6:
    """Context manager to push the Font Awesome 6 font for the current frame.
    If the font is not loaded, it will be loaded (and will appear on the next frame)"""

    def __init__(self) -> None:
        # return
        if _FONT_AWESOME_6 is None:
            # Fonts need to be loaded before the new frame starts,
            hello_imgui.get_runner_params().callbacks.after_swap = functional_utils.sequence_void_functions(
                hello_imgui.get_runner_params().callbacks.after_swap, _load_font_awesome_6
            )

    def __enter__(self):
        if _FONT_AWESOME_6 is not None:
            # pass
            imgui.push_font(_FONT_AWESOME_6)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if _FONT_AWESOME_6 is not None:
                # pass
                imgui.pop_font()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginEnd context", exc_info=(exc_type, exc_val, exc_tb))


def fontawesome_6_ctx():
    return PushFontAwesome6()


__all__ = ["fontawesome_6_ctx", "icons_fontawesome_6"]
