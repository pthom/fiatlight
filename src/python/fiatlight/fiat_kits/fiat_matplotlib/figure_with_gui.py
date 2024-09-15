import logging

from matplotlib.figure import Figure

from imgui_bundle import ImVec2, imgui_fig, imgui, hello_imgui, portable_file_dialogs as pfd
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6


class FigureWithGui(AnyDataWithGui[Figure]):
    """A Gui that can present a resizable matplotlib figure"""

    _figure_size: ImVec2
    should_refresh_fig: bool = False
    _save_file_dialog: pfd.save_file | None = None
    _last_fig_id: int | None = None

    def __init__(self) -> None:
        super().__init__(Figure)
        self._figure_size = ImVec2(0, 0)
        self.callbacks.present = self._present

        self.callbacks.save_gui_options_to_json = self._save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self._load_gui_options_from_json
        self.callbacks.on_change = self._on_change

    def _present(self, figure: Figure) -> None:
        self.should_refresh_fig = self._last_fig_id != id(figure)
        self._last_fig_id = id(figure)

        imgui_fig.fig("##Figure", figure, self._figure_size, refresh_image=self.should_refresh_fig)
        self.should_refresh_fig = False

        # Handle saving
        with fontawesome_6_ctx():
            cursor_pos = imgui.get_cursor_screen_pos()
            fig_pos = imgui.get_item_rect_min()
            margin = hello_imgui.em_size(0.3)
            imgui.set_cursor_screen_pos(ImVec2(fig_pos.x + margin, fig_pos.y + margin))
            if imgui.button(icons_fontawesome_6.ICON_FA_FLOPPY_DISK):
                self._save_file_dialog = pfd.save_file(
                    "Save figure as image", "", ["*.png", "*.jpg", "*.jpeg", "*.gif"]
                )
            imgui.set_cursor_screen_pos(cursor_pos)
        if self._save_file_dialog is not None and self._save_file_dialog.ready():
            file_path = self._save_file_dialog.result()
            if file_path:
                try:
                    figure.savefig(file_path)
                except Exception as e:
                    logging.error(f"Failed to save figure: {e}")
            self._save_file_dialog = None

    def _save_gui_options_to_json(self) -> JsonDict:
        return {"figure_size": self._figure_size.to_dict()}

    def _load_gui_options_from_json(self, options: JsonDict) -> None:
        if "figure_size" in options:
            self._figure_size = ImVec2.from_dict(options["figure_size"])

    def _on_change(self, _fig: Figure) -> None:
        self.should_refresh_fig = True


def _register_figure_with_gui() -> None:
    from fiatlight.fiat_togui.gui_registry import register_type

    register_type(Figure, FigureWithGui)
