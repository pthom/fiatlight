import fiatlight
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd, icons_fontawesome_6, fontawesome_6_ctx  # noqa
from fiatlight.fiat_togui.str_with_resizable_gui import StrWithResizableGui
from imgui_bundle import imgui, imgui_ctx
from .prompt import Prompt


class PromptWithGui(AnyDataWithGui[Prompt]):
    _str_with_resizable_gui: StrWithResizableGui
    _edited_prompt: Prompt  # not yet submitted

    def __init__(self) -> None:
        super().__init__()
        self._str_with_resizable_gui = StrWithResizableGui()
        self._edited_prompt = Prompt("")
        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.edit_popup_possible = True
        self.callbacks.present_custom = self.present_custom
        self.callbacks.default_value_provider = lambda: Prompt("")
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

    def on_change(self, prompt: Prompt) -> None:
        self._edited_prompt = prompt
        self._str_with_resizable_gui.on_change(prompt)

    def save_gui_options_to_json(self) -> JsonDict:
        r = {
            "_str_with_resizable_gui": self._str_with_resizable_gui.save_gui_options_to_json(),
        }
        return r

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        if "_str_with_resizable_gui" in json:
            self._str_with_resizable_gui.load_gui_options_from_json(json["_str_with_resizable_gui"])

    def present_custom(self, prompt: Prompt) -> None:
        self._str_with_resizable_gui.present_custom(prompt)

    def edit(self, prompt: Prompt) -> tuple[bool, Prompt]:
        fire_change = False
        with fontawesome_6_ctx():
            is_in_node = fiatlight.is_rendering_in_node()
            if is_in_node:
                with imgui_ctx.begin_horizontal("Prompt"):
                    _edited_prompt_changed, self._edited_prompt = self._str_with_resizable_gui.edit(self._edited_prompt)
                    if imgui.button("Submit"):
                        fire_change = True
            else:
                with imgui_ctx.begin_vertical("Prompt"):
                    _edited_prompt_changed, self._edited_prompt = self._str_with_resizable_gui.edit(self._edited_prompt)
                    if imgui.button("Submit"):
                        fire_change = True

        if fire_change:
            return True, self._edited_prompt
        else:
            return False, prompt


def _register_prompt() -> None:
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(Prompt, PromptWithGui)
