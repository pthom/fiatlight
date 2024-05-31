import fiatlight
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui, PossibleCustomAttributes
from fiatlight.fiat_types.base_types import CustomAttributesDict
from fiatlight.fiat_widgets import fiat_osd, icons_fontawesome_6, fontawesome_6_ctx, text_maybe_truncated
from imgui_bundle import imgui, imgui_ctx, hello_imgui, ImVec2
from pydantic import BaseModel


class StrPossibleCustomAttributes(PossibleCustomAttributes):
    """PossibleCustomAttributes for StrWithGui"""

    def __init__(self) -> None:
        super().__init__("StrWithGui")

        self.add_explained_attribute(
            name="width_em",
            type_=float,
            explanation="Initial width of the text input (in em unit). Can be saved if resizable is True",
            default_value=15.0,
        )
        self.add_explained_attribute(
            name="hint",
            type_=str,
            explanation="Hint text for the input",
            default_value="",
        )
        self.add_explained_attribute(
            name="allow_multiline",
            type_=bool,
            explanation="Whether the user can edit the string as multiline string in a popup",
            default_value=False,
        )
        self.add_explained_attribute(
            name="resizable",
            type_=bool,
            explanation="Whether the single line widget is resizable",
            default_value=True,
        )


_STR_POSSIBLE_CUSTOM_ATTRIBUTES = StrPossibleCustomAttributes()


class StrWithGuiParams(BaseModel):
    """Parameters for StrWithGui"""

    # Saved parameters (user pref)
    width_em: float = 15.0  # single line editing width

    # Developer parameters (not saved)
    resizable: bool = True  # single line widget is resizable
    hint: str = ""  # hint text for the input (single line)
    allow_multiline: bool = False  # whether the user can edit the string as multiline string in a popup


class StrWithGui(AnyDataWithGui[str]):
    """A Gui for a string with resizable input text, with a popup for multiline editing."""

    params: StrWithGuiParams

    _input_text_in_node: hello_imgui.InputTextData
    _input_text_in_popup: hello_imgui.InputTextData

    def __init__(self) -> None:
        super().__init__(str)
        self.params = StrWithGuiParams()
        self._input_text_in_node = hello_imgui.InputTextData("", multiline=False, size_em=ImVec2(15, 0))
        self._input_text_in_popup = hello_imgui.InputTextData("", multiline=True, size_em=ImVec2(60, 15))
        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.edit_popup_possible = False
        self.callbacks.present_custom = self.present_custom
        self.callbacks.present_custom_popup_possible = True
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        self.callbacks.on_custom_attrs_changed = self.on_custom_attrs_changed

    def on_change(self, value: str) -> None:
        self._input_text_in_node.text = value
        self._input_text_in_popup.text = value

    def on_custom_attrs_changed(self, custom_attrs: CustomAttributesDict) -> None:
        if "width_em" in custom_attrs:
            self.params.width_em = custom_attrs["width_em"]
        if "hint" in custom_attrs:
            self.params.hint = custom_attrs["hint"]
        if "allow_multiline" in custom_attrs:
            self.params.allow_multiline = custom_attrs["allow_multiline"]
        if "resizable" in custom_attrs:
            self.params.resizable = custom_attrs["resizable"]
        self._update_internal_state_from_params()

    def _update_internal_state_from_params(self) -> None:
        self._input_text_in_node.size_em.x = self.params.width_em
        self._input_text_in_node.hint = self.params.hint
        self.callbacks.edit_popup_possible = self.params.allow_multiline
        self._input_text_in_node.resizable = self.params.resizable

    @staticmethod
    def possible_custom_attributes() -> PossibleCustomAttributes | None:
        return _STR_POSSIBLE_CUSTOM_ATTRIBUTES

    def save_gui_options_to_json(self) -> JsonDict:
        # We only save the width (the other parameters are decided by the developer, not the user)
        if self.params.resizable:
            return {"width_em": self.params.width_em}
        else:
            return {}

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        if self.params.resizable and "width_em" in json:
            self.params.width_em = json["width_em"]
            self._update_internal_state_from_params()

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
                    if self.params.allow_multiline:
                        # Display a small icon to indicate that a popup is available
                        imgui.text(icons_fontawesome_6.ICON_FA_CIRCLE_INFO)
                        fiat_osd.set_widget_tooltip(
                            "Open popup to edit a multiline string (see button on top of this input)"
                        )
                    changed = hello_imgui.input_text_resizable("##StringNode", self._input_text_in_node)
                    self.params.width_em = self._input_text_in_node.size_em.x
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
