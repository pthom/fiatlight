"""Rotated text rendering.

imgui has no native rotated text, so `draw_text_rotated_90` rotates the glyph
vertices the draw list just emitted (the standard ImRotate trick). It reserves the
rotated bounding box in the layout, so it composes with `begin_horizontal` /
`begin_vertical` and node-editor node sizing.
"""
from imgui_bundle import imgui, ImVec2


def draw_text_rotated_90(text: str, clockwise: bool = True, color_u32: int | None = None) -> ImVec2:
    """Draw `text` rotated ±90° at the current cursor and reserve its (rotated)
    bounding box in the layout. Returns the reserved size.

    `color_u32` defaults to the current `Text` color. `clockwise=True` reads
    top→bottom; `clockwise=False` reads bottom→top.
    """
    if color_u32 is None:
        color_u32 = imgui.get_color_u32(imgui.Col_.text.value)

    dl = imgui.get_window_draw_list()
    text_size = imgui.calc_text_size(text)
    origin = imgui.get_cursor_screen_pos()

    i0 = dl.vtx_buffer.size()
    dl.add_text(origin, color_u32, text)
    i1 = dl.vtx_buffer.size()

    # Rotate by ±90° around `origin` (cos(±90)=0, sin(±90)=±1), then translate so
    # the rotated box sits at the cursor (going down-right) for clean layout.
    sin_a = 1.0 if clockwise else -1.0
    off_x = text_size.y if clockwise else 0.0
    off_y = 0.0 if clockwise else text_size.x
    vb = dl.vtx_buffer
    for i in range(i0, i1):
        v = vb[i]
        dx = v.pos.x - origin.x
        dy = v.pos.y - origin.y
        v.pos = ImVec2(origin.x - dy * sin_a + off_x, origin.y + dx * sin_a + off_y)

    reserved = ImVec2(text_size.y, text_size.x)
    imgui.dummy(reserved)
    return reserved
