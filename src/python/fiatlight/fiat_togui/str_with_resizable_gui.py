import fiatlight
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd, icons_fontawesome_6, fontawesome_6_ctx, text_maybe_truncated
from imgui_bundle import imgui, imgui_ctx, hello_imgui, ImVec2


class StrWithResizableGui(AnyDataWithGui[str]):
    """A Gui for a string with resizable input text, with a popup for multiline editing."""

    _input_text_in_node: hello_imgui.InputTextData
    _input_text_in_popup: hello_imgui.InputTextData

    def __init__(self) -> None:
        super().__init__(str)
        self._input_text_in_node = hello_imgui.InputTextData("", multiline=False, size_em=ImVec2(15, 0))
        self._input_text_in_popup = hello_imgui.InputTextData("", multiline=True, size_em=ImVec2(60, 15))
        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.edit_popup_possible = True
        self.callbacks.present_custom = self.present_custom
        self.callbacks.present_custom_popup_possible = True
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

    def on_change(self, value: str) -> None:
        self._input_text_in_node.text = value
        self._input_text_in_popup.text = value

    def save_gui_options_to_json(self) -> JsonDict:
        r = {
            "_input_text_in_node_size": self._input_text_in_node.size_em.to_dict(),
            "_input_text_in_popup_size": self._input_text_in_popup.size_em.to_dict(),
        }
        return r

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        if "_input_text_in_node_size" in json:
            self._input_text_in_node.size_em = ImVec2.from_dict(json["_input_text_in_node_size"])
        if "_input_text_in_popup_size" in json:
            self._input_text_in_popup.size_em = ImVec2.from_dict(json["_input_text_in_popup_size"])

    @staticmethod
    def present_custom(text_value: str) -> None:
        if fiatlight.is_rendering_in_window():
            text_edit_size = ImVec2(
                imgui.get_window_width() - hello_imgui.em_size(1), imgui.get_window_height() - hello_imgui.em_size(5)
            )
            imgui.input_text_multiline("##str", text_value, text_edit_size, imgui.InputTextFlags_.read_only.value)
        else:
            text_maybe_truncated(
                text_value,
                max_width_chars=50,
                max_lines=5,
            )

    def edit(self, value: str) -> tuple[bool, str]:
        if not isinstance(value, str):
            raise ValueError(f"StrWithResizableGui expects a string, got: {type(value)}")
        changed: bool
        with fontawesome_6_ctx():
            is_in_node = fiatlight.is_rendering_in_node()
            if is_in_node:
                with imgui_ctx.begin_horizontal("String"):
                    # Display a small icon to indicate that a popup is available
                    imgui.text(icons_fontawesome_6.ICON_FA_CIRCLE_INFO)
                    fiat_osd.set_widget_tooltip(
                        "Open popup to edit a multiline string (see button on top of this input)"
                    )
                    # The prompt editor
                    changed = hello_imgui.input_text_resizable("##StringNode", self._input_text_in_node)
                    if changed:
                        value = self._input_text_in_node.text
                        self._input_text_in_popup.text = value
            else:
                with imgui_ctx.begin_vertical("Prompt"):
                    changed = hello_imgui.input_text_resizable("##StringPopup", self._input_text_in_popup)
                    window_width = imgui.get_window_width()
                    window_width_em = hello_imgui.pixel_size_to_em(window_width)
                    self._input_text_in_popup.size_em.x = window_width_em - 3.0
                    if changed:
                        value = self._input_text_in_popup.text
                        self._input_text_in_node.text = value

        return changed, value
