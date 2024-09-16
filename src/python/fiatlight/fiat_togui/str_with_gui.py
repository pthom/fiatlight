import fiatlight
from fiatlight.fiat_types import JsonDict
from fiatlight.fiat_core import AnyDataWithGui, PossibleFiatAttributes
from fiatlight.fiat_types.base_types import FiatAttributes
from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_widgets import fiat_osd, icons_fontawesome_6, fontawesome_6_ctx, text_maybe_truncated
from imgui_bundle import imgui, imgui_ctx, hello_imgui, ImVec2
from pydantic import BaseModel
import textwrap


def _textwrap_preserve_line_breaks(s: str, width: int) -> str:
    wrapped_text = "\n".join(textwrap.fill(line, width=width) for line in s.splitlines())
    return wrapped_text


class StrPossibleFiatAttributes(PossibleFiatAttributes):
    """PossibleFiatAttributes for StrWithGui"""

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
            name="allow_multiline_edit",
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
        self.add_explained_attribute(
            name="wrap_multiline",
            type_=bool,
            explanation="Whether the text is wrapped when presented as a multiline string",
            default_value=False,
        )
        self.add_explained_attribute(
            name="wrap_multiline_width",
            type_=int,
            explanation="Width at which the text is wrapped when presented as a multiline string",
            default_value=80,
        )


_STR_POSSIBLE_FIAT_ATTRIBUTES = StrPossibleFiatAttributes()


def _lines_max_width(text: str) -> int:
    lines = text.splitlines()
    max_width = max(len(line) for line in lines)
    return max_width


class StrWithGuiUserParams(BaseModel):
    # Saved parameters (user pref)
    width_em: float = 15.0  # single line editing width
    size_multiline_em: tuple[float, float] = (60.0, 15.0)  # multiline editing size
    wrap_multiline: bool = False  # whether the text is wrapped when presented as a multiline string
    wrap_multiline_width: int = 80


class StrWithGuiDeveloperParams(BaseModel):
    # Developer parameters (not saved)
    resizable: bool = True  # single line widget is resizable
    hint: str = ""  # hint text for the input (single line)
    allow_multiline_edit: bool = False  # whether the user can edit the string as multiline string in a popup


class StrWithGuiParams(BaseModel):
    """Parameters for StrWithGui"""

    # Saved parameters (user pref)
    user_params: StrWithGuiUserParams = StrWithGuiUserParams()
    # Developer parameters (not saved)
    developer_params: StrWithGuiDeveloperParams = StrWithGuiDeveloperParams()


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
        self.callbacks.edit_node_compatible = True
        self.callbacks.present = self.present
        self.callbacks.present_node_compatible = True
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changes

        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    @staticmethod
    def _shall_present_in_multiline_text_edit(text: str) -> bool:
        nb_lines = text.count("\n") + 1
        if nb_lines >= 2:
            return True
        if len(text) > 80:
            return True
        return False

    def on_change(self, value: str) -> None:
        self._store_text_value_in_cache(value)

    def _store_text_value_in_cache(self, value: str) -> None:
        self._input_text_in_node.text = value
        self._input_text_classic.text = value

        if self._shall_present_in_multiline_text_edit(value):
            self.callbacks.present_collapsible = True

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        if "width_em" in fiat_attrs:
            self.params.user_params.width_em = fiat_attrs["width_em"]
        if "hint" in fiat_attrs:
            self.params.developer_params.hint = fiat_attrs["hint"]
        if "allow_multiline_edit" in fiat_attrs:
            self.params.developer_params.allow_multiline_edit = fiat_attrs["allow_multiline_edit"]
            self.callbacks.present_collapsible = self.params.developer_params.allow_multiline_edit
            self.callbacks.edit_collapsible = self.params.developer_params.allow_multiline_edit
            self.callbacks.edit_node_compatible = not self.params.developer_params.allow_multiline_edit
        if "resizable" in fiat_attrs:
            self.params.developer_params.resizable = fiat_attrs["resizable"]
        if "wrap_multiline" in fiat_attrs:
            self.params.user_params.wrap_multiline = fiat_attrs["wrap_multiline"]
        if "wrap_multiline_width" in fiat_attrs:
            self.params.user_params.wrap_multiline_width = fiat_attrs["wrap_multiline_width"]
        self._update_internal_state_from_params()

    def _update_internal_state_from_params(self) -> None:
        self._input_text_in_node.size_em.x = self.params.user_params.width_em
        self._input_text_in_node.hint = self.params.developer_params.hint
        self.callbacks.edit_node_compatible = not self.params.developer_params.allow_multiline_edit
        self._input_text_in_node.resizable = self.params.developer_params.resizable

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _STR_POSSIBLE_FIAT_ATTRIBUTES

    def save_gui_options_to_json(self) -> JsonDict:
        return self.params.user_params.model_dump(mode="json")

    def load_gui_options_from_json(self, json: JsonDict) -> None:
        self.params.user_params = StrWithGuiUserParams.model_validate(json)

    def present(self, text_value: str) -> None:
        # We need to change the cache: on_change is not called when the value is Invalid,
        # but we want the user to be able to correct an invalid value)
        self._store_text_value_in_cache(text_value)

        if not fiatlight.is_rendering_in_node():
            text_edit_size = ImVec2(
                imgui.get_window_width() - hello_imgui.em_size(3), imgui.get_window_height() - hello_imgui.em_size(4)
            )
            if StrWithGui._shall_present_in_multiline_text_edit(text_value):
                can_wrap = _lines_max_width(text_value) > self.params.user_params.wrap_multiline_width
                if can_wrap:
                    _, self.params.user_params.wrap_multiline = imgui.checkbox(
                        "Wrap text", self.params.user_params.wrap_multiline
                    )
                    imgui.same_line()
                    imgui.set_next_item_width(hello_imgui.em_size(10))
                    _, self.params.user_params.wrap_multiline_width = imgui.slider_int(
                        "Wrap width", self.params.user_params.wrap_multiline_width, 40, 200
                    )
                    text_edit_size.y -= hello_imgui.em_size(1.5)
                if self.params.user_params.wrap_multiline:
                    # text_value = textwrap.fill(text_value, self.params.user_params.wrap_multiline_width)
                    # text_value = "\n".join(textwrap.wrap(text_value, self.params.user_params.wrap_multiline_width))
                    # text_value = "\n".join(textwrap.fill(text_value, self.params.user_params.wrap_multiline_width))
                    text_value = _textwrap_preserve_line_breaks(
                        text_value, self.params.user_params.wrap_multiline_width
                    )
                imgui.input_text_multiline("##str", text_value, text_edit_size, imgui.InputTextFlags_.read_only.value)
            else:
                imgui.text(text_value)
        else:
            text_maybe_truncated(text_value, get_fiat_config().style.str_truncation.str_expanded_in_node)

    def edit(self, value: str) -> tuple[bool, str]:
        if not isinstance(value, str):
            raise ValueError(f"StrWithResizableGui expects a string, got: {type(value)}")

        # We need to change the cache: on_change is not called when the value is Invalid,
        # but we want the user to be able to correct an invalid value)
        self._store_text_value_in_cache(value)

        changed: bool
        with fontawesome_6_ctx():
            is_in_node = fiatlight.is_rendering_in_node()
            if is_in_node:
                with imgui_ctx.begin_horizontal("String"):
                    if self.params.developer_params.allow_multiline_edit:
                        # Display a small icon to indicate that a popup is available
                        imgui.text(icons_fontawesome_6.ICON_FA_CIRCLE_INFO)
                        fiat_osd.set_widget_tooltip(
                            "Open popup to edit a multiline string (see button on top of this input)"
                        )
                    changed = hello_imgui.input_text_resizable("##StringNode", self._input_text_in_node)
                    self.params.user_params.width_em = self._input_text_in_node.size_em.x
                    if changed:
                        value = self._input_text_in_node.text
                        self._input_text_classic.text = value
            else:
                with imgui_ctx.begin_vertical("StrEditPopup"):
                    # Set editing mode for the input text
                    self._input_text_classic.multiline = self.params.developer_params.allow_multiline_edit
                    # Set size of the input text (depends on the mode)
                    if self.params.developer_params.allow_multiline_edit:
                        self._input_text_classic.size_em = ImVec2(*self.params.user_params.size_multiline_em)
                    else:
                        self._input_text_classic.size_em = ImVec2(self.params.user_params.width_em, 0)

                    # Special case: if we are in a detached window, we need to adjust the width of the input text
                    if not fiatlight.is_rendering_in_node():
                        window_width = imgui.get_window_width()
                        window_width_em = hello_imgui.pixel_size_to_em(window_width)
                        self._input_text_classic.size_em.x = window_width_em - 12.0

                        was_resizable_in_node = self._input_text_classic.resizable
                        self._input_text_classic.resizable = False
                        changed = hello_imgui.input_text_resizable("##StringPopup", self._input_text_classic)
                        self._input_text_classic.resizable = was_resizable_in_node
                    else:
                        changed = hello_imgui.input_text_resizable("##StringPopup", self._input_text_classic)

                    # update params if resized
                    if self.params.developer_params.allow_multiline_edit:
                        self.params.user_params.size_multiline_em = (
                            self._input_text_classic.size_em.x,
                            self._input_text_classic.size_em.y,
                        )
                    else:
                        self.params.user_params.width_em = self._input_text_classic.size_em.x

                    if changed:
                        value = self._input_text_classic.text
                        self._input_text_in_node.text = value

        return changed, value
