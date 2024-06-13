import fiatlight
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui, PossibleCustomAttributes
from fiatlight.fiat_types.base_types import FiatAttributes
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
            explanation="Initial width of the single line text input (in em unit). Can be saved if resizable is True",
            default_value=15.0,
        )
        self.add_explained_attribute(
            name="size_multiline_em",
            type_=tuple,
            explanation="Initial size of the multiline text input (in em unit)",
            default_value=(60.0, 15.0),
            tuple_types=(float, float),
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
            explanation="Whether the user can edit the string as multiline string (when not in a function node)",
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
    size_multiline_em: tuple[float, float] = (60.0, 15.0)  # multiline editing size

    # Developer parameters (not saved)
    resizable: bool = True  # single line widget is resizable
    hint: str = ""  # hint text for the input (single line)
    allow_multiline: bool = False  # whether the user can edit the string as multiline string in a popup


class StrWithGui(AnyDataWithGui[str]):
    """A Gui for a string with resizable input text, with a popup for multiline editing."""

    params: StrWithGuiParams

    _input_text_in_node: hello_imgui.InputTextData
    _input_text_classic: hello_imgui.InputTextData

    def __init__(self) -> None:
        super().__init__(str)
        self.params = StrWithGuiParams()
        self._input_text_in_node = hello_imgui.InputTextData("", multiline=False, size_em=ImVec2(15, 0))
        self._input_text_classic = hello_imgui.InputTextData("", multiline=False, size_em=ImVec2(15, 0))
        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.edit_popup_possible = False
        self.callbacks.present = self.present
        self.callbacks.present_popup_possible = True
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        self.callbacks.on_custom_attrs_changed = self.on_custom_attrs_changed

        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    def on_change(self, value: str) -> None:
        self._input_text_in_node.text = value
        self._input_text_classic.text = value

        nb_lines = value.count("\n") + 1
        if nb_lines >= 2:
            self.callbacks.present_collapsible = True

    def on_custom_attrs_changed(self, custom_attrs: FiatAttributes) -> None:
        if "width_em" in custom_attrs:
            self.params.width_em = custom_attrs["width_em"]
        if "hint" in custom_attrs:
            self.params.hint = custom_attrs["hint"]
        if "allow_multiline" in custom_attrs:
            self.params.allow_multiline = custom_attrs["allow_multiline"]
            self.callbacks.present_collapsible = self.params.allow_multiline
            self.callbacks.edit_collapsible = self.params.allow_multiline
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
    def present(text_value: str) -> None:
        if fiatlight.is_rendering_in_fiatlight_detached_window():
            text_edit_size = ImVec2(
                imgui.get_window_width() - hello_imgui.em_size(1), imgui.get_window_height() - hello_imgui.em_size(5)
            )
            nb_lines = text_value.count("\n") + 1
            if nb_lines > 5:
                imgui.input_text_multiline("##str", text_value, text_edit_size, imgui.InputTextFlags_.read_only.value)
            else:
                imgui.text(text_value)
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
                        self._input_text_classic.text = value
            else:
                with imgui_ctx.begin_vertical("StrEditPopup"):
                    # Set editing mode for the input text
                    self._input_text_classic.multiline = self.params.allow_multiline
                    # Set size of the input text (depends on the mode)
                    if self.params.allow_multiline:
                        self._input_text_classic.size_em = ImVec2(*self.params.size_multiline_em)
                    else:
                        self._input_text_classic.size_em = ImVec2(self.params.width_em, 0)

                    # Special case: if we are in a detached window, we need to adjust the width of the input text
                    if fiatlight.is_rendering_in_fiatlight_detached_window():
                        window_width = imgui.get_window_width()
                        window_width_em = hello_imgui.pixel_size_to_em(window_width)
                        self._input_text_classic.size_em.x = window_width_em - 3.0

                    # Display the widget
                    changed = hello_imgui.input_text_resizable("##StringPopup", self._input_text_classic)

                    # update params if resized
                    if self.params.allow_multiline:
                        self.params.size_multiline_em = (
                            self._input_text_classic.size_em.x,
                            self._input_text_classic.size_em.y,
                        )
                    else:
                        self.params.width_em = self._input_text_classic.size_em.x

                    if changed:
                        value = self._input_text_classic.text
                        self._input_text_in_node.text = value

        return changed, value
