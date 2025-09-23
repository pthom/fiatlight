import fiatlight
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd, icons_fontawesome_6, fontawesome_6_ctx  # noqa
from fiatlight.fiat_togui.str_with_gui import StrWithGui
from imgui_bundle import imgui, imgui_ctx
from .prompt import Prompt


class PromptWithGui(AnyDataWithGui[Prompt]):
    """A Gui to edit a prompt, with a Submit button, and a multiline edit in a popup."""

    _str_with_resizable_gui: StrWithGui
    _submit_continuously: bool = False
    _edited_prompt: Prompt  # not yet submitted

    def __init__(self) -> None:
        super().__init__(Prompt)
        self._str_with_resizable_gui = StrWithGui()
        self._str_with_resizable_gui.params.developer_params.hint = "Enter a prompt"
        self._str_with_resizable_gui.params.developer_params.allow_multiline_edit = True
        self._str_with_resizable_gui.params.developer_params.resizable = True

        self._edited_prompt = Prompt("")
        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.edit_node_compatible = False
        self.callbacks.edit_collapsible = False
        self.callbacks.present = self.present
        self.callbacks.default_value_provider = lambda: Prompt("")
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

    def on_change(self, prompt: Prompt) -> None:
        self._edited_prompt = prompt
        self._str_with_resizable_gui.on_change(prompt)

    def save_gui_options_to_json(self) -> JsonDict:
        r = {
            "_str_with_resizable_gui": self._str_with_resizable_gui.save_gui_options_to_json(),
            "submit_continuously": self._submit_continuously,
        }
        return r

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        if "_str_with_resizable_gui" in json:
            self._str_with_resizable_gui.load_gui_options_from_json(json["_str_with_resizable_gui"])
        if "submit_continuously" in json:
            self._submit_continuously = json["submit_continuously"]

    def present(self, prompt: Prompt) -> None:
        self._str_with_resizable_gui.present(prompt)

    def edit(self, prompt: Prompt) -> tuple[bool, Prompt]:
        fire_change = False
        with fontawesome_6_ctx():
            is_in_node = fiatlight.is_rendering_in_node()
            if is_in_node:
                return False, prompt  # no edit GUI in node
            else:
                with imgui_ctx.begin_vertical("Prompt"):
                    _edited_prompt_changed, self._edited_prompt = self._str_with_resizable_gui.edit(self._edited_prompt)  # type: ignore
                    with imgui_ctx.begin_horizontal("Prompt"):
                        if imgui.button("Submit"):
                            fire_change = True
                        imgui.spring()
                        _, self._submit_continuously = imgui.checkbox("Submit continuously", self._submit_continuously)
                    if _edited_prompt_changed and self._submit_continuously:
                        fire_change = True

        if fire_change:
            return True, self._edited_prompt
        else:
            return False, prompt


def _register_prompt() -> None:
    from fiatlight.fiat_togui.gui_registry import register_typing_new_type

    register_typing_new_type(Prompt, PromptWithGui)
