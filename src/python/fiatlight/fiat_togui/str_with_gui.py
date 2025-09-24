from fiatlight.fiat_core import AnyDataWithGui, PossibleFiatAttributes
from fiatlight.fiat_types.base_types import FiatAttributes
from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_widgets import text_maybe_truncated
from imgui_bundle import imgui, hello_imgui
from pydantic import BaseModel


class StrPossibleFiatAttributes(PossibleFiatAttributes):
    """PossibleFiatAttributes for StrWithGui"""

    def __init__(self) -> None:
        super().__init__("StrWithGui")

        self.add_explained_attribute(
            name="width_em",
            type_=float,
            explanation="Width of the single line text input (in em unit)",
            default_value=15.0,
        )
        self.add_explained_attribute(
            name="allow_multiline_edit",
            type_=bool,
            explanation="Whether the user can edit the string as multiline string",
            default_value=False,
        )
        self.add_explained_attribute(
            name="size_multiline_em",
            type_=tuple,
            explanation="Size of the multiline text input (in em unit)",
            default_value=(50.0, 15.0),
            tuple_types=(float, float),
        )
        self.add_explained_attribute(
            name="hint",
            type_=str,
            explanation="Hint text for the input",
            default_value="",
        )


_STR_POSSIBLE_FIAT_ATTRIBUTES = StrPossibleFiatAttributes()


def _lines_max_width(text: str) -> int:
    lines = text.splitlines()
    max_width = max(len(line) for line in lines)
    return max_width


class StrWithGuiParams(BaseModel):
    hint: str = ""  # hint text for the input (single line)
    allow_multiline_edit: bool = False  # whether the user can edit the string as multiline string in a popup
    width_em: float = 15.0  # single line editing width
    size_multiline_em: tuple[float, float] = (50.0, 15.0)  # multiline editing size


class StrWithGui(AnyDataWithGui[str]):
    """A Gui for a string with resizable input text, with a popup for multiline editing."""

    params: StrWithGuiParams

    def __init__(self) -> None:
        super().__init__(str)
        self.params = StrWithGuiParams()
        self.callbacks.on_change = self.on_change
        self.callbacks.edit = self.edit
        self.callbacks.present = self.present
        self.callbacks.default_value_provider = lambda: ""
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changes

        self.callbacks.present_collapsible = False
        self.callbacks.edit_collapsible = False

    def on_change(self, value: str) -> None:
        pass

    def on_fiat_attributes_changes(self, fiat_attrs: FiatAttributes) -> None:
        if "width_em" in fiat_attrs:
            self.params.width_em = fiat_attrs["width_em"]
        if "size_multiline_em" in fiat_attrs:
            self.params.size_multiline_em = fiat_attrs["size_multiline_em"]
        if "hint" in fiat_attrs:
            self.params.hint = fiat_attrs["hint"]
        if "allow_multiline_edit" in fiat_attrs:
            self.params.allow_multiline_edit = fiat_attrs["allow_multiline_edit"]

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        return _STR_POSSIBLE_FIAT_ATTRIBUTES

    def present(self, text_value: str) -> None:
        text_maybe_truncated(text_value, get_fiat_config().style.str_truncation.str_expanded_in_node)

    def edit(self, value: str) -> tuple[bool, str]:
        if not isinstance(value, str):
            raise ValueError(f"StrWithResizableGui expects a string, got: {type(value)}")
        changed: bool
        if self.params.allow_multiline_edit:
            size_multiline_px = hello_imgui.em_to_vec2(self.params.size_multiline_em)
            width_singleline_px = hello_imgui.em_size(self.params.width_em)
            imgui.set_next_item_width(width_singleline_px)
            changed, value = imgui.input_text_multiline("##text", value, size_multiline_px)
        else:
            imgui.set_next_item_width(hello_imgui.em_size(self.params.width_em))
            changed, value = imgui.input_text_with_hint("##text", self.params.hint, value)

        return changed, value
