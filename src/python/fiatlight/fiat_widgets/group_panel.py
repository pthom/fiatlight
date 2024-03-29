# Adapted from ImmVision (imgui_imm.cpp)

from imgui_bundle import imgui, ImVec2

from typing import List, Any

ImRect = imgui.internal.ImRect


s_GroupPanelLabelStack: List[ImRect] = []


def begin_group_panel(name: str, size: ImVec2 | None = None) -> None:
    if size is None:
        size = ImVec2(0.0, 0.0)

    imgui.begin_group()

    item_spacing = imgui.get_style().item_spacing
    imgui.push_style_var(imgui.StyleVar_.frame_padding.value, ImVec2(0.0, 0.0))
    imgui.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(0.0, 0.0))

    frame_height = imgui.get_frame_height()
    imgui.begin_group()

    effective_size = size
    if effective_size.x < 0.0:
        effective_size.x = imgui.get_window_width()
    else:
        effective_size.x = size.x
    imgui.dummy(ImVec2(effective_size.x, 0.0))

    imgui.dummy(ImVec2(frame_height * 0.5, 0.0))
    imgui.same_line(0.0, 0.0)
    imgui.begin_group()
    imgui.dummy(ImVec2(frame_height * 0.5, 0.0))
    imgui.same_line(0.0, 0.0)
    if len(name) > 0:
        imgui.text_unformatted(name)

    label_min = imgui.get_item_rect_min()
    label_max = imgui.get_item_rect_max()
    imgui.same_line(0.0, 0.0)
    imgui.dummy(ImVec2(0.0, frame_height + item_spacing.y))
    imgui.begin_group()

    imgui.pop_style_var(2)

    imgui.internal.get_current_window().content_region_rect.max.x -= frame_height * 0.5
    imgui.internal.get_current_window().work_rect.max.x -= frame_height * 0.5
    imgui.internal.get_current_window().inner_rect.max.x -= frame_height * 0.5

    imgui.internal.get_current_window().size.x -= frame_height

    item_width = imgui.calc_item_width()
    imgui.push_item_width(max(0.0, item_width - frame_height))

    s_GroupPanelLabelStack.append(ImRect(label_min, label_max))


def end_group_panel() -> None:
    imgui.pop_item_width()

    item_spacing = imgui.get_style().item_spacing

    imgui.push_style_var(imgui.StyleVar_.frame_padding.value, ImVec2(0.0, 0.0))
    imgui.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(0.0, 0.0))

    frame_height = imgui.get_frame_height()

    imgui.end_group()

    imgui.end_group()

    imgui.same_line(0.0, 0.0)
    imgui.dummy(ImVec2(frame_height * 0.5, 0.0))
    imgui.dummy(ImVec2(0.0, frame_height - frame_height * 0.5 - item_spacing.y))

    imgui.end_group()

    item_min = imgui.get_item_rect_min()
    item_max = imgui.get_item_rect_max()

    label_rect = s_GroupPanelLabelStack.pop()

    half_frame = ImVec2(frame_height * 0.25 * 0.5, frame_height * 0.5)
    frame_rect = ImRect(
        ImVec2(item_min.x + half_frame.x, item_min.y + half_frame.y), ImVec2(item_max.x - half_frame.x, item_max.y)
    )
    label_rect.min.x -= item_spacing.x
    label_rect.max.x += item_spacing.x

    for i in range(4):
        if i == 0:
            # left half-plane
            imgui.push_clip_rect(ImVec2(-float("inf"), -float("inf")), ImVec2(label_rect.min.x, float("inf")), True)
        elif i == 1:
            # right half-plane
            imgui.push_clip_rect(ImVec2(label_rect.max.x, -float("inf")), ImVec2(float("inf"), float("inf")), True)
        elif i == 2:
            # top
            imgui.push_clip_rect(
                ImVec2(label_rect.min.x, -float("inf")), ImVec2(label_rect.max.x, label_rect.min.y), True
            )
        elif i == 3:
            # bottom
            imgui.push_clip_rect(
                ImVec2(label_rect.min.x, label_rect.max.y), ImVec2(label_rect.max.x, float("inf")), True
            )

        color_vec4 = imgui.get_style_color_vec4(imgui.Col_.border.value)
        color_imu32 = imgui.get_color_u32(color_vec4)
        imgui.get_window_draw_list().add_rect(frame_rect.min, frame_rect.max, color_imu32, half_frame.x)

        imgui.pop_clip_rect()

    imgui.pop_style_var(2)

    imgui.internal.get_current_window().content_region_rect.max.x += frame_height * 0.5
    imgui.internal.get_current_window().work_rect.max.x += frame_height * 0.5
    imgui.internal.get_current_window().inner_rect.max.x += frame_height * 0.5

    imgui.internal.get_current_window().size.x += frame_height

    imgui.dummy(ImVec2(0.0, 0.0))

    imgui.end_group()


# Context manager for group panel
class _BeginGroupPanel:
    def __init__(self, name: str, size: ImVec2 | None = None) -> None:
        self.name = name
        self.size = size

    def __enter__(self) -> None:
        begin_group_panel(self.name, self.size)

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        end_group_panel()


def begin_group_panel_ctx(name: str, size: ImVec2 | None = None) -> _BeginGroupPanel:
    return _BeginGroupPanel(name, size)


def sandbox() -> None:
    from imgui_bundle import hello_imgui, imgui_ctx

    def gui() -> None:
        with begin_group_panel_ctx("Group Panel"):
            with imgui_ctx.begin_horizontal("H"):
                with imgui_ctx.begin_vertical("V"):
                    imgui.text("Hello, World!")
                    imgui.text("Ahh")
                imgui.button("Button")

    hello_imgui.run(gui)


if __name__ == "__main__":
    sandbox()
