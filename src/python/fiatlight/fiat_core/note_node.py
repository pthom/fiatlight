"""NoteNode: an editable markdown / post-it note that can be added to a graph.

The markdown (with LaTeX) is rendered inside the node; the text is edited in a detached
window, because the canvas rule forbids complex widgets inside ed.begin/end. The text is a
serializable param, so it is saved with the workspace and carried by copy/paste.

(MarkdownNode stays the read-only documentation node whose text comes from code.)
"""

from fiatlight.fiat_core.gui_node import GuiNode
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_md, hello_imgui, ImVec2
from pydantic import BaseModel


class _NoteParams(BaseModel):
    md_string: str = ""
    text_width_em: float = 16.0


_NOTE_PLACEHOLDER = "*Empty note — click the edit button.*"


class NoteNode(GuiNode):
    """An editable markdown note (post-it). Renders markdown + LaTeX in the node; the edit button
    opens a popup to edit the text. The text is saved with the workspace."""

    note_params: _NoteParams

    def __init__(self, md_string: str = "", label: str = "Note", text_width_em: float = 16.0) -> None:
        self.note_params = _NoteParams(md_string=md_string, text_width_em=text_width_em)
        super().__init__(self.gui, label=label, gui_serializable_data=self.note_params)
        # function_name drives the palette name (GuiNode would otherwise use the method name "gui").
        self.function_name = label

    def gui(self) -> None:
        width_pixels = hello_imgui.em_size(self.note_params.text_width_em)
        imgui.dummy(ImVec2(width_pixels, 1))  # keep a minimum width even for short / empty notes
        imgui_md.render_unindented(self.note_params.md_string or _NOTE_PLACEHOLDER)
        # Editing must happen outside ed.begin/end -> a detached window (the button is in-node OK).
        fiat_osd.show_void_detached_window_button(
            fiat_osd.DetachedWindowParams(
                unique_id="##note_edit_" + str(id(self)),
                window_name=f"Edit note##{id(self)}",
                gui_function=self._edit_gui,
                button_label="Edit",
                window_size=hello_imgui.em_to_vec2(32.0, 20.0),
            )
        )

    def _edit_gui(self) -> None:
        changed, new_text = imgui.input_text_multiline(
            "##note_text", self.note_params.md_string, hello_imgui.em_to_vec2(30.0, 16.0)
        )
        if changed:
            self.note_params.md_string = new_text
