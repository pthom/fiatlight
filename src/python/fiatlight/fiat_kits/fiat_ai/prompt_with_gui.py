from fiatlight.fiat_core import AnyDataWithGui, PossibleFiatAttributes
from fiatlight.fiat_types.base_types import FiatAttributes
from fiatlight.fiat_widgets import fiat_osd, icons_fontawesome_6, fontawesome_6_ctx  # noqa
from fiatlight.fiat_togui.str_with_gui import StrWithGui, _STR_POSSIBLE_FIAT_ATTRIBUTES
from imgui_bundle import imgui, imgui_ctx
from .prompt import Prompt


class PromptWithGui(AnyDataWithGui[Prompt]):
    """A Gui to edit a prompt, with a Submit button, and a multiline edit in a popup."""

    _str_gui: StrWithGui
    _edited_prompt: Prompt  # not yet submitted

    def __init__(self) -> None:
        super().__init__(Prompt)
        self._str_gui = StrWithGui()
        self._str_gui.params.hint = "Enter a prompt"
        self._str_gui.params.allow_multiline_edit = True

        self._edited_prompt = Prompt("")
        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.edit_collapsible = False
        self.callbacks.present = self.present
        self.callbacks.default_value_provider = lambda: Prompt("")

        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changes

    def on_change(self, prompt: Prompt) -> None:
        self._edited_prompt = prompt
        self._str_gui.on_change(prompt)

    def present(self, prompt: Prompt) -> None:
        self._str_gui.present(prompt)

    def edit(self, prompt: Prompt) -> tuple[bool, Prompt]:
        with imgui_ctx.begin_horizontal("Prompt"):
            edited, new_prompt = self._str_gui.edit(self._edited_prompt)
            if edited:
                self._edited_prompt = Prompt(new_prompt)
            imgui.spring()

            is_changed = prompt != self._edited_prompt
            if is_changed:
                if imgui.button("Submit"):
                    return True, self._edited_prompt
                else:
                    return False, prompt
            else:
                imgui.begin_disabled(True)
                imgui.button("Submit")
                imgui.end_disabled()
                return False, prompt

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _STR_POSSIBLE_FIAT_ATTRIBUTES

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        self._str_gui.on_fiat_attributes_changes(fiat_attrs)


def _register_prompt() -> None:
    from fiatlight.fiat_togui.gui_registry import register_typing_new_type

    register_typing_new_type(Prompt, PromptWithGui)
