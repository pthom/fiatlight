"""MarkdownNode: A node that simply renders a Markdown text.
It is implemented as a GuiNode with an internal gui function.
"""
from fiatlight.fiat_core.gui_node import GuiNode
from imgui_bundle import imgui, imgui_md, hello_imgui, ImVec2
from pydantic import BaseModel


def _empty_bool_function() -> bool:
    return False


class _MarkdownParams(BaseModel):
    text_width_em: float = 20.0
    unindented: bool = True
    md_string: str


class MarkdownNode(GuiNode):
    """A node that simply renders a Markdown text, optionally resizable.
    If resizable is True, the user can resize the node to change the text width,
    and the new width will be saved and restored upon restarting the application.
    """

    md_params: _MarkdownParams

    def __init__(
        self,
        md_string: str,
        label: str = "Documentation",
        text_width_em: float = 20.0,
        unindented: bool = True,
    ) -> None:
        self.md_params = _MarkdownParams(unindented=unindented, md_string=md_string, text_width_em=text_width_em)

        super().__init__(self.gui, label=label)

    def gui(self) -> None:
        width_pixels = hello_imgui.em_size(self.md_params.text_width_em)
        imgui.dummy(ImVec2(width_pixels, 1))
        if self.md_params.unindented:
            imgui_md.render_unindented(self.md_params.md_string)
        else:
            imgui_md.render(self.md_params.md_string)
