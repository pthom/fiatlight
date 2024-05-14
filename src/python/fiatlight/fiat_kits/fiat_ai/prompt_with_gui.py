import fiatlight
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd, icons_fontawesome_6, fontawesome_6_ctx  # noqa
from imgui_bundle import imgui, imgui_ctx, hello_imgui, ImVec2
from .prompt import Prompt


class PromptWithGui(AnyDataWithGui[Prompt]):
    _prompt_input_in_node: hello_imgui.InputTextData
    _prompt_input_in_popup: hello_imgui.InputTextData

    def __init__(self) -> None:
        super().__init__()
        self._prompt_input_in_node = hello_imgui.InputTextData("", multiline=False, size_em=ImVec2(20, 0))
        self._prompt_input_in_popup = hello_imgui.InputTextData("", multiline=True, size_em=ImVec2(60, 15))
        self.callbacks.on_change = self._on_change
        self.callbacks.edit = self._edit
        self.callbacks.edit_popup_possible = True
        self.callbacks.present_custom = self._present_custom
        self.callbacks.default_value_provider = lambda: Prompt("")
        self.callbacks.save_gui_options_to_json = self._save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self._load_gui_options_from_json

    def _on_change(self, prompt: Prompt) -> None:
        self._prompt_input_in_node.text = prompt
        self._prompt_input_in_popup.text = prompt

    def _save_gui_options_to_json(self) -> JsonDict:
        r = {
            "prompt_input_in_node_size": self._prompt_input_in_node.size_em.to_dict(),
            "prompt_input_in_popup_size": self._prompt_input_in_popup.size_em.to_dict(),
        }
        return r

    def _load_gui_options_from_json(self, json: JsonDict) -> None:
        if "prompt_input_in_node_size" in json:
            self._prompt_input_in_node.size_em = ImVec2.from_dict(json["prompt_input_in_node_size"])
        if "prompt_input_in_popup_size" in json:
            self._prompt_input_in_popup.size_em = ImVec2.from_dict(json["prompt_input_in_popup_size"])

    @staticmethod
    def _present_custom(prompt: Prompt) -> None:
        # Display a summary of the prompt: the first 80 characters
        max_len = 80
        text_summary = prompt[:max_len] + "..." if len(prompt) > max_len else prompt
        text_summary = text_summary.replace("\n", "\\n")
        imgui.text(text_summary)

    def _edit(self, original_prompt: Prompt) -> tuple[bool, Prompt]:
        fire_change = False
        with fontawesome_6_ctx():
            is_in_node = fiatlight.is_rendering_in_node()
            if is_in_node:
                with imgui_ctx.begin_horizontal("Prompt"):
                    # Display a small icon to indicate that a popup is available
                    imgui.text(icons_fontawesome_6.ICON_FA_CIRCLE_INFO)
                    fiat_osd.set_widget_tooltip(
                        "Open popup to edit a multiline prompt (see button on top of this input)"
                    )
                    # The prompt editor
                    changed = hello_imgui.input_text_resizable("##PromptNode", self._prompt_input_in_node)
                    if changed:
                        self._prompt_input_in_popup.text = self._prompt_input_in_node.text
                    # A button to register the change
                    if imgui.button("Submit"):
                        fire_change = True
            else:
                with imgui_ctx.begin_vertical("Prompt"):
                    changed = hello_imgui.input_text_resizable("##PromptPopup", self._prompt_input_in_popup)
                    window_width = imgui.get_window_width()
                    window_width_em = hello_imgui.pixel_size_to_em(window_width)
                    self._prompt_input_in_popup.size_em.x = window_width_em - 3.0
                    if changed:
                        self._prompt_input_in_node.text = self._prompt_input_in_popup.text
                    if imgui.button("Submit"):
                        fire_change = True

        if fire_change:
            prompt_text = self._prompt_input_in_popup.text if not is_in_node else self._prompt_input_in_node.text
            return True, Prompt(prompt_text)
        else:
            return False, original_prompt


def _register_prompt() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(Prompt, PromptWithGui)
