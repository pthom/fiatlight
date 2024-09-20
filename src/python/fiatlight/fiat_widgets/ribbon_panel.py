from fiatlight.fiat_types.function_types import GuiFunction
from imgui_bundle import imgui, ImVec2, hello_imgui, imgui_ctx


def vertical_separator() -> None:
    screen_cursor_pos = imgui.get_cursor_screen_pos()
    window = imgui.internal.get_current_window()
    y_top = imgui.get_window_pos().y + hello_imgui.em_size(0.2)
    y_bottom = imgui.get_window_pos().y + imgui.get_window_height() - hello_imgui.em_size(0.3)
    window.draw_list.add_line(
        ImVec2(screen_cursor_pos.x, y_top),
        ImVec2(screen_cursor_pos.x, y_bottom),
        imgui.get_color_u32(imgui.Col_.separator.value),
        1.0,
    )

    # update cursor position
    cursor_pos = imgui.get_cursor_screen_pos()
    cursor_pos.x += imgui.get_style().item_spacing.x
    imgui.set_cursor_screen_pos(cursor_pos)


def ribbon_panel(title: str, gui: GuiFunction) -> None:
    with imgui_ctx.push_id(title):
        with imgui_ctx.begin_vertical("RibbonV"):
            with imgui_ctx.begin_horizontal("guiH", None, align=0.5):
                with imgui_ctx.begin_vertical("guiV"):
                    gui()

            # Move the title closer to the gui
            cursor_pos = imgui.get_cursor_screen_pos()
            cursor_pos.y -= imgui.get_style().item_spacing.y * 0.7
            imgui.set_cursor_screen_pos(cursor_pos)

            # Draw the title, centered
            with imgui_ctx.begin_horizontal("RibbonH", None):
                with imgui_ctx.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(0, 0)):
                    imgui.spring()
                # Make the title look disabled
                with imgui_ctx.push_style_color(
                    imgui.Col_.text.value, imgui.get_style_color_vec4(imgui.Col_.text_disabled.value)
                ):
                    imgui.text(title)


def sandbox() -> None:
    def gui() -> None:
        imgui.set_next_window_size(ImVec2(400, 100), imgui.Cond_.appearing.value)

        def panel_gui() -> None:
            with imgui_ctx.begin_horizontal("H"):
                imgui.button("AHHH")
                imgui.checkbox("Check", True)

        with imgui_ctx.begin("GUI"):
            with imgui_ctx.begin_horizontal("panelssH"):
                ribbon_panel("Ribbon Panel", panel_gui)
                vertical_separator()
                with imgui_ctx.push_id("a"):
                    ribbon_panel("Ribbon Panel", panel_gui)
                # ribbon_panel("Ribbon Panel", panel_gui)

    hello_imgui.run(gui)


if __name__ == "__main__":
    sandbox()
