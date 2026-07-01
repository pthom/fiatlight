"""NoteNode: an editable markdown / post-it note that can be added to a graph.

The markdown (with LaTeX) is rendered inside the node; the text is edited in a popup opened
from the node (imgui popups work inside ed.begin/end). The text is a serializable param, so
it is saved with the workspace and carried by copy/paste.

(MarkdownNode stays the read-only documentation node whose text comes from code.)
"""

from fiatlight.fiat_core.gui_node import GuiNode
from fiatlight.fiat_widgets.fontawesome6_ctx_utils import icons_fontawesome_6, fontawesome_6_ctx
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
    _MIN_WIDTH_EM = 10.0
    _MAX_WIDTH_EM = 120.0

    def __init__(self, md_string: str = "", label: str = "Note", text_width_em: float = 16.0) -> None:
        self.note_params = _NoteParams(md_string=md_string, text_width_em=text_width_em)
        super().__init__(self.gui, label=label, gui_serializable_data=self.note_params)
        # function_name drives the palette name (GuiNode would otherwise use the method name "gui").
        self.function_name = label

    def gui(self) -> None:
        content_x0 = imgui.get_cursor_pos_x()
        width_pixels = hello_imgui.em_size(self.note_params.text_width_em)
        imgui.dummy(ImVec2(width_pixels, 1))  # keep a minimum width even for short / empty notes
        imgui_md.render_unindented(self.note_params.md_string or _NOTE_PLACEHOLDER)

        popup_id = f"note_edit_{id(self)}"
        if imgui.button("Edit"):
            imgui.open_popup(popup_id)
        imgui.same_line()
        self._draw_width_grip(content_x0, width_pixels)
        if imgui.begin_popup(popup_id):
            self._edit_gui()
            imgui.end_popup()

    def _draw_width_grip(self, content_x0: float, width_pixels: float) -> None:
        """A resize grip at the note's right edge: drag it horizontally to set the width.

        Inside ed.begin/end the mouse delta is already in canvas (logical) coordinates, the same
        space as width_pixels, so the grip tracks the cursor at any zoom. Width is saved with the note.
        """
        grip_w = hello_imgui.em_size(1.5)
        imgui.set_cursor_pos_x(content_x0 + width_pixels - grip_w)
        with fontawesome_6_ctx():
            imgui.button(icons_fontawesome_6.ICON_FA_LEFT_RIGHT + f"##note_grip_{id(self)}", ImVec2(grip_w, 0.0))
        if imgui.is_item_active():
            new_em = (width_pixels + imgui.get_io().mouse_delta.x) / hello_imgui.em_size(1.0)
            self.note_params.text_width_em = self._clamp_width_em(new_em)
        if imgui.is_item_hovered() or imgui.is_item_active():
            imgui.set_mouse_cursor(imgui.MouseCursor_.resize_ew.value)

    def _clamp_width_em(self, width_em: float) -> float:
        return float(min(self._MAX_WIDTH_EM, max(self._MIN_WIDTH_EM, width_em)))

    def _edit_gui(self) -> None:
        # Width drives the in-node markdown wrapping (the dummy above); editing it live updates the
        # node preview, and it is saved with the note. (The in-node grip does the same by dragging.)
        width_changed, new_width = imgui.slider_float(
            "Width (em)", self.note_params.text_width_em, self._MIN_WIDTH_EM, self._MAX_WIDTH_EM
        )
        if width_changed:
            self.note_params.text_width_em = self._clamp_width_em(new_width)

        changed, new_text = imgui.input_text_multiline(
            "##note_text", self.note_params.md_string, hello_imgui.em_to_vec2(30.0, 16.0)
        )
        if changed:
            self.note_params.md_string = new_text
