from fiatlight.fiat_core import AnyDataWithGui, PossibleFiatAttributes
from fiatlight.fiat_types.base_types import FiatAttributes
from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_widgets import text_maybe_truncated
from imgui_bundle import hello_imgui, ImVec2


class StrPossibleFiatAttributes(PossibleFiatAttributes):
    """PossibleFiatAttributes for StrWithGui"""

    def __init__(self) -> None:
        super().__init__("StrWithGui")

        self.add_explained_attribute(
            name="hint",
            type_=str,
            explanation="Hint text for the input",
            default_value="",
        )
        self.add_explained_attribute(
            name="multiline",
            type_=bool,
            explanation="Whether the user can edit the string as multiline string",
            default_value=False,
        )
        self.add_explained_attribute(
            name="size_em",
            type_=tuple,
            explanation="Size of the text input (in em unit). Height used only if allow_multiline_edit is True",
            default_value=(15.0, 3.0),
            tuple_types=(float, float),
        )
        self.add_explained_attribute(
            name="resizable",
            type_=bool,
            explanation="Whether the input text is resizable",
            default_value=True,
        )


_STR_POSSIBLE_FIAT_ATTRIBUTES = StrPossibleFiatAttributes()


def _lines_max_width(text: str) -> int:
    lines = text.splitlines()
    max_width = max(len(line) for line in lines)
    return max_width


class StrWithGui(AnyDataWithGui[str]):
    """A Gui for a string with resizable input text, with a popup for multiline editing."""

    # params: StrWithGuiParams
    _input_text_data: hello_imgui.InputTextData

    def __init__(self) -> None:
        super().__init__(str)

        self._input_text_data = hello_imgui.InputTextData()
        self._input_text_data.resizable = True
        self._input_text_data.size_em = ImVec2(15.0, 3.0)

        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.present = self.present
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changes

        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    def on_change(self, value: str) -> None:
        self._input_text_data.text = value

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        if "size_em" in fiat_attrs:
            size_em = fiat_attrs["size_em"]
            assert (
                isinstance(size_em, (tuple, list)) and len(size_em) == 2
            ), "size_em must be a tuple or list of length 2"
            self._input_text_data.size_em = ImVec2(size_em[0], size_em[1])
        if "hint" in fiat_attrs:
            self._input_text_data.hint = fiat_attrs["hint"]
        if "multiline" in fiat_attrs:
            self._input_text_data.multiline = fiat_attrs["multiline"]
        if "resizable" in fiat_attrs:
            self._input_text_data.resizable = fiat_attrs["resizable"]

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _STR_POSSIBLE_FIAT_ATTRIBUTES

    def present(self, text_value: str) -> None:
        text_maybe_truncated(text_value, get_fiat_config().style.str_truncation.str_expanded_in_node)

    def edit(self, value: str) -> tuple[bool, str]:
        if not isinstance(value, str):
            raise ValueError(f"StrWithResizableGui expects a string, got: {type(value)}")
        changed = hello_imgui.input_text_resizable("##text", self._input_text_data)
        return changed, self._input_text_data.text
